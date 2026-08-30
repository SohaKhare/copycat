"""
One entry point for every direct Gemini call, with:

- multi-key failover - set GEMINI_API_KEY plus optionally GEMINI_API_KEY_2,
  GEMINI_API_KEY_3, ... (or a comma-separated GEMINI_API_KEYS). On a 429
  RESOURCE_EXHAUSTED / quota error the next key is tried. Free-tier quota is
  per project, so a second project's key genuinely doubles throughput - which
  matters at a hackathon where everyone shares the same models.
- retry/backoff per key (backend.ai.retry.gemini_retry) for transient
  429/503/5xx.

Callers: ai/gemini.py, ai/skill_resolver.py, ai/planner.py, ai/voice.py.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError, ClientError

from backend.ai.retry import gemini_retry
from backend.logging_setup import log

load_dotenv()


def get_gemini_keys() -> list[str]:
    """All configured Gemini keys, in priority order, de-duplicated."""

    keys: list[str] = []

    combined = os.getenv("GEMINI_API_KEYS", "")
    if combined:
        keys.extend(part.strip() for part in combined.split(",") if part.strip())

    single = os.getenv("GEMINI_API_KEY")
    if single:
        keys.append(single.strip())

    index = 2
    while True:
        extra = os.getenv(f"GEMINI_API_KEY_{index}")
        if not extra:
            break
        keys.append(extra.strip())
        index += 1

    seen: set[str] = set()
    ordered: list[str] = []
    for key in keys:
        if key not in seen:
            seen.add(key)
            ordered.append(key)

    if not ordered:
        raise ValueError("No GEMINI_API_KEY found in the environment.")

    return ordered


def _is_quota_error(error: BaseException) -> bool:
    return isinstance(error, (ClientError, APIError)) and getattr(
        error, "code", None
    ) == 429


def call_gemini(*, model: str, contents, config=None):
    """
    Run models.generate_content against the first key that isn't rate-limited.

    Each key gets the full gemini_retry backoff before we move on. If every key
    is exhausted, the last error is re-raised (a ClientError 429, which the API
    layer turns into a clean 429 response).
    """

    keys = get_gemini_keys()
    last_error: BaseException | None = None

    for position, key in enumerate(keys):
        client = genai.Client(api_key=key)

        call = gemini_retry(client.models.generate_content)
        kwargs = {"model": model, "contents": contents}
        if config is not None:
            kwargs["config"] = config

        try:
            return call(**kwargs)
        except (ClientError, APIError) as error:
            last_error = error
            if _is_quota_error(error) and position < len(keys) - 1:
                log.warning(
                    "Gemini key #%d rate-limited on %s; trying next key",
                    position + 1,
                    model,
                )
                continue
            raise

    assert last_error is not None
    raise last_error
