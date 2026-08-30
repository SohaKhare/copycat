"""
Retry/backoff for direct Gemini calls (ai/gemini.py, ai/skill_resolver.py,
ai/planner.py's Windows branch, ai/voice.py). These use google.genai.Client()
directly rather than going through ADK, so they don't get ADK's built-in retry
handling - without this, a 429/503 just crashes the request as a bare 500.

Retries:
- 429 (rate limit) - ClientError
- 503 UNAVAILABLE / 500 / 502 / 504 (model overloaded, transient) - ServerError
Does NOT retry other 4xx (bad request, bad key, invalid audio) - those won't
get better on a retry.
"""

from google.genai.errors import APIError, ClientError, ServerError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


def _is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, ClientError):
        return exception.code == 429
    if isinstance(exception, ServerError):
        return True
    if isinstance(exception, APIError):
        return exception.code in (429, 500, 502, 503, 504)
    return False


# Kept deliberately short: on the interactive path a fast, clear failure beats a
# two-minute spinner. Multi-key failover (ai/gemini_client.py) adds the breadth.
gemini_retry = retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=15),
    reraise=True,
)
