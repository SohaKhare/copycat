"""
Builds the ADK agent that executes a browser skill's goal through
Playwright MCP tools. The agent reasons live against the actual page state
(navigate -> snapshot -> click/type -> observe -> repeat) rather than
following a rigid pre-scripted plan, since DOM structure and element refs
aren't known until the page actually loads.
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from backend.executors.browser_permission import make_permission_gate
from backend.executors.browser_tools import build_browser_toolset
from backend.executors.clipboard_tool import set_clipboard

load_dotenv()

# LiteLLM's Anthropic provider looks specifically for an env var literally
# named ANTHROPIC_API_KEY to auto-authenticate - it won't pick up a generic
# API_KEY. Bridge it here so this project can still keep a single key in
# .env instead of duplicating it under two names.
if os.getenv("API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = os.environ["API_KEY"]

# Model is configurable via MODEL_NAME in .env, e.g. "anthropic/claude-sonnet-4-5"
# or "gemini/gemini-3.1-flash-lite". Gemini models route through ADK's native
# Gemini class instead of LiteLLM - it's what ADK itself recommends over
# LiteLLM for Gemini, and it's the only path that gets our retry/backoff for
# transient 429/503s. Everything else (Anthropic, etc.) goes through LiteLLM.
MODEL_NAME = os.getenv("MODEL_NAME", "anthropic/claude-sonnet-4-5")

GEMINI_RETRY_OPTIONS = types.HttpRetryOptions(
    attempts=6,
    initial_delay=5,
    max_delay=60,
    exp_base=1.5,
    jitter=2,
    http_status_codes=[429, 500, 502, 503, 504],
)


def _build_model(model_name: str):
    if model_name.startswith("gemini/"):
        bare_model_name = model_name.removeprefix("gemini/")
        api_key = os.environ.get("GEMINI_API_KEY")
        return Gemini(
            model=bare_model_name,
            client_kwargs={"api_key": api_key} if api_key else {},
            retry_options=GEMINI_RETRY_OPTIONS,
        )

    return LiteLlm(model=model_name)

INSTRUCTION = (
    "You are a browser automation agent for CopyCat. You have Playwright "
    "browser tools available: browser_navigate, browser_snapshot, "
    "browser_click, browser_type, browser_wait_for, and others. Always call "
    "browser_snapshot after navigating or after an action that changes the "
    "page, before trying to click/type anything - it gives you the current "
    "element refs. Work step by step. If a tool call comes back with an "
    "'error' about missing permission, stop trying that action and report "
    "it plainly in your final answer instead of retrying it.\n\n"
    "If a step says to 'copy' something (a response, a value, any text), do "
    "NOT click the site's own copy button - it doesn't reliably reach the "
    "real clipboard when running headless. Instead, read the exact text "
    "from the page (via browser_snapshot) and call the set_clipboard tool "
    "with that exact text. That's the only way copying actually works.\n\n"
    "When the task is complete, give one short, clear final summary of "
    "what you did."
)


def build_browser_agent(
    *,
    model_name: str = MODEL_NAME,
    allowed_tools: set[str] | None = None,
) -> LlmAgent:
    return LlmAgent(
        name="copycat_browser_executor",
        model=_build_model(model_name),
        instruction=INSTRUCTION,
        tools=[build_browser_toolset(), set_clipboard],
        before_tool_callback=make_permission_gate(allowed_tools),
    )
