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
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.genai import types

from backend.env_config import (
    get_anthropic_api_key,
    get_gemini_api_keys,
    get_groq_api_key,
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
    "You are a browser automation agent for CopyCat. Be fast and direct.\n\n"
    "Speed rules:\n"
    "- Prefer a deep-link over UI search. Gmail keyword search is "
    "https://mail.google.com/mail/u/0/#search/QUERY (URL-encode spaces).\n"
    "- If the current page already matches the next step, do not navigate again.\n"
    "- One snapshot after a page change is enough. Do not snapshot the full "
    "Gmail inbox — go to the search URL first.\n"
    "- Never use browser_find. Use browser_type / browser_click on refs from "
    "the latest snapshot.\n"
    "- Do not use browser_evaluate unless type/click already failed twice.\n"
    "- Complete all sub-tasks in one session. Do not restart the browser.\n"
    "- If a tool returns a permission error, stop retrying that exact action.\n"
    "- ChatGPT / other chat UIs: type into the composer with submit=true, then "
    "browser_wait_for the reply, then snapshot and read the assistant message.\n\n"
    "Final reply (critical):\n"
    "- Your last message MUST be the content the user asked for: the emails, "
    "the ChatGPT summary, the message list — quoted or paraphrased in full.\n"
    "- Never describe what you did. Do not write 'I searched', 'I provided', "
    "or 'I successfully'.\n"
    "- If ChatGPT fails, still return the facts you already read (sender, "
    "subject, and what each email says).\n"
    "- Use a short numbered list when there are multiple items.\n"
    "- Also call set_clipboard with that same findings text so it is preserved."
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

    if resolved_name.startswith("groq/"):
        api_key = get_groq_api_key()
        if not api_key:
            raise ValueError(
                "MODEL_NAME points to Groq but GROQ_API_KEY is not set."
            )
        return LiteLlm(model=resolved_name, api_key=api_key)

    raise ValueError(
        f"Unsupported MODEL_NAME '{resolved_name}'. "
        "Use gemini/..., groq/..., anthropic/..., or openai/... with a matching API key."
    )


def build_browser_agent(
    *,
    model_name: str | None = None,
    allowed_tools: set[str] | None = None,
) -> tuple[LlmAgent, McpToolset]:
    toolset = build_browser_toolset()
    agent = LlmAgent(
        name="copycat_browser_executor",
        model=_build_model(model_name),
        instruction=INSTRUCTION,
        tools=[toolset, set_clipboard],
        before_tool_callback=make_permission_gate(allowed_tools),
    )
    return agent, toolset
