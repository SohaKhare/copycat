"""
Retry/backoff for direct Gemini calls (ai/gemini.py, ai/skill_resolver.py,
ai/planner.py's Windows branch). These use google.genai.Client() directly
rather than going through ADK, so they don't get ADK's built-in retry
handling - without this, a 429 just crashes the request as a bare 500.
"""

from google.genai.errors import ClientError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


def _is_rate_limit_error(exception: BaseException) -> bool:
    return isinstance(exception, ClientError) and exception.code == 429


gemini_retry = retry(
    retry=retry_if_exception(_is_rate_limit_error),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    reraise=True,
)
