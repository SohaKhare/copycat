"""
One entry point for every direct Gemini call, with:

- multi-key failover - set GEMINI_API_KEY plus optionally GEMINI_API_KEY_2,
  GEMINI_API_KEY_3, ... (or a comma-separated GEMINI_API_KEYS). On a 429
  quota error OR a 503/5xx overload, the next key is tried. Extra keys only
  help if they belong to a different Google Cloud project.
- if every key is overloaded on the requested model, fall back to another
  Gemini flash model that is often still serving.
- retry/backoff per key (backend.ai.retry.gemini_retry) for transient
  429/503/5xx.

Callers: ai/gemini.py, ai/skill_resolver.py, ai/planner.py, ai/voice.py.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError, ClientError, ServerError

from backend.ai.groq_client import _flatten_text_contents, call_groq_text
from backend.ai.retry import gemini_retry
from backend.env_config import get_groq_api_key
from backend.logging_setup import log

load_dotenv()

_FALLBACK_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
)


def _clean_key(value: str) -> str:
    return value.strip().strip('"').strip("'")


def get_gemini_keys() -> list[str]:
    """All configured Gemini keys, in priority order, de-duplicated."""

    keys: list[str] = []

    combined = os.getenv("GEMINI_API_KEYS", "")
    if combined:
        keys.extend(
            _clean_key(part) for part in combined.split(",") if _clean_key(part)
        )

    single = os.getenv("GEMINI_API_KEY")
    if single:
        keys.append(_clean_key(single))

    index = 2
    while True:
        extra = os.getenv(f"GEMINI_API_KEY_{index}")
        if not extra:
            break
        keys.append(_clean_key(extra))
        index += 1

    seen: set[str] = set()
    ordered: list[str] = []
    for key in keys:
        if key and key not in seen:
            seen.add(key)
            ordered.append(key)

    if not ordered:
        raise ValueError("No GEMINI_API_KEY found in the environment.")

    return ordered


def _error_code(error: BaseException) -> int | None:
    return getattr(error, "code", None)


def _should_failover(error: BaseException) -> bool:
    if not isinstance(error, (ClientError, ServerError, APIError)):
        return False
    return _error_code(error) in (429, 500, 502, 503, 504)


def _models_to_try(requested: str) -> list[str]:
    bare = requested.removeprefix("gemini/")
    models = [bare]
    for fallback in _FALLBACK_MODELS:
        if fallback not in models:
            models.append(fallback)
    return models


def call_gemini(*, model: str, contents, config=None):
    """
    Run models.generate_content against the first key/model that works.

    Text-only calls use Groq first when GROQ_API_KEY is set (Gemini 503
    workaround). Image/audio calls stay on Gemini.
    """

    groq_key = get_groq_api_key()
    text_only = _flatten_text_contents(contents)
    if groq_key and text_only is not None and config is None:
        try:
            return call_groq_text(contents)
        except Exception as error:
            log.warning("Groq text call failed (%s); falling back to Gemini", error)

    try:
        keys = get_gemini_keys()
    except ValueError:
        keys = []

    if not keys:
        if groq_key and text_only is not None:
            return call_groq_text(contents)
        raise ValueError("No GEMINI_API_KEY or GROQ_API_KEY found.")

    models = _models_to_try(model)
    last_error: BaseException | None = None

    log.info("Gemini call model=%s keys=%d", models[0], len(keys))

    for model_index, model_name in enumerate(models):
        for position, key in enumerate(keys):
            client = genai.Client(api_key=key)
            call = gemini_retry(client.models.generate_content)
            kwargs = {"model": model_name, "contents": contents}
            if config is not None:
                kwargs["config"] = config

            try:
                return call(**kwargs)
            except (ClientError, ServerError, APIError) as error:
                last_error = error
                more_keys = position < len(keys) - 1
                more_models = model_index < len(models) - 1
                if _should_failover(error) and (more_keys or more_models):
                    log.warning(
                        "Gemini %s on %s with key #%d/%d; trying next",
                        _error_code(error),
                        model_name,
                        position + 1,
                        len(keys),
                    )
                    continue
                raise

    assert last_error is not None
    raise last_error


def create_gemini_client() -> genai.Client:
    """Return a Gemini client using the primary configured API key."""

    return genai.Client(api_key=get_gemini_keys()[0])
