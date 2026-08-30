"""
Builds the ADK agent that executes a browser skill's goal through
Playwright MCP tools. The agent reasons live against the actual page state
(navigate -> snapshot -> click/type -> observe -> repeat) rather than
following a rigid pre-scripted plan, since DOM structure and element refs
aren't known until the page actually loads.
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from backend.env_config import (
    get_anthropic_api_key,
    get_gemini_api_keys,
    get_openai_api_key,
    resolve_browser_model_name,
)
from backend.executors.browser_permission import make_permission_gate
from backend.executors.browser_tools import build_browser_toolset
from backend.executors.clipboard_tool import set_clipboard

GEMINI_RETRY_OPTIONS = types.HttpRetryOptions(
    attempts=6,
    initial_delay=5,
    max_delay=60,
    exp_base=1.5,
    jitter=2,
    http_status_codes=[429, 500, 502, 503, 504],
)

INSTRUCTION = (
    "You are a browser automation agent for CopyCat. You have Playwright "
    "browser tools: browser_navigate, browser_snapshot, browser_click, "
    "browser_type, browser_wait_for, and others.\n\n"
    "Rules:\n"
    "- Complete all sub-tasks in one session without restarting the browser.\n"
    "- Minimize snapshots — only call browser_snapshot when you need element "
    "refs before a click or type.\n"
    "- Work step by step. Do not repeat navigation already done for prior "
    "sub-tasks.\n"
    "- If a tool returns a permission error, stop retrying it and report it.\n"
    "- To copy text: read it from browser_snapshot and call set_clipboard; "
    "do not use site copy buttons.\n"
    "- When finished, give one short summary (one line per sub-task if "
    "multiple)."
)


def _build_model(model_name: str | None = None):
    resolved_name = model_name or resolve_browser_model_name()

    if resolved_name.startswith("gemini/"):
        bare_model_name = resolved_name.removeprefix("gemini/")
        keys = get_gemini_api_keys()
        if not keys:
            raise ValueError(
                "Browser executor requires GEMINI_API_KEY but none is configured."
            )
        return Gemini(
            model=bare_model_name,
            client_kwargs={"api_key": keys[0]},
            retry_options=GEMINI_RETRY_OPTIONS,
        )

    if resolved_name.startswith("anthropic/"):
        api_key = get_anthropic_api_key()
        if not api_key:
            raise ValueError(
                "MODEL_NAME points to Anthropic but ANTHROPIC_API_KEY is not set."
            )
        return LiteLlm(model=resolved_name, api_key=api_key)

    if resolved_name.startswith("openai/") or resolved_name.startswith("gpt-"):
        api_key = get_openai_api_key()
        if not api_key:
            raise ValueError(
                "MODEL_NAME points to OpenAI but OPENAI_API_KEY is not set."
            )
        return LiteLlm(model=resolved_name, api_key=api_key)

    raise ValueError(
        f"Unsupported MODEL_NAME '{resolved_name}'. "
        "Use gemini/..., anthropic/..., or openai/... with a matching API key."
    )


def build_browser_agent(
    *,
    model_name: str | None = None,
    allowed_tools: set[str] | None = None,
) -> LlmAgent:
    return LlmAgent(
        name="copycat_browser_executor",
        model=_build_model(model_name),
        instruction=INSTRUCTION,
        tools=[build_browser_toolset(), set_clipboard],
        before_tool_callback=make_permission_gate(allowed_tools),
    )
