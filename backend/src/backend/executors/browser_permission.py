"""
Permission gate for browser tool calls - the "user controls what the AI is
allowed to access and do" principle from the CopyCat/Apprentice design.

MVP heuristic, not a full security boundary: Playwright MCP's browser_click
takes an `element` field that's a human-readable description of what's being
clicked (the MCP server itself documents it as used to obtain permission to
interact with the element), so we scan that plus the tool name for
sensitive-action keywords and block them before they run.
"""

from typing import Any

from backend.logging_setup import log

ALWAYS_CONFIRM_KEYWORDS = (
    "delete",
    "remove",
    "purchase",
    "buy",
    "pay",
    "checkout",
    "send",
    "confirm order",
    "unsubscribe",
)


def make_permission_gate(allowed_tools: set[str] | None = None):
    """
    Returns a `before_tool_callback` for LlmAgent.

    allowed_tools: if given, any MCP tool name not in this set is blocked
    outright. If None, all tools are allowed except the always-confirm
    keywords below.
    """

    async def gate(tool, args: dict[str, Any], tool_context):
        name = tool.name

        if allowed_tools is not None and name not in allowed_tools:
            log.warning(
                "[copycat.browser] blocked tool=%r reason=not_in_allowed_list args=%s",
                name,
                args,
            )
            return {
                "error": (
                    f"'{name}' is outside this skill's approved tool list "
                    f"{sorted(allowed_tools)}. Blocked - ask the user to "
                    "approve this capability first."
                )
            }

        # Only scan the tool name and the human-facing target, not JS
        # payloads — "send-button" in a ChatGPT evaluate was blocking
        # the real submit and adding extra retries.
        haystack_parts = [name]
        for key in ("element", "target", "name"):
            value = args.get(key)
            if isinstance(value, str):
                haystack_parts.append(value)
        haystack = " ".join(haystack_parts).lower()

        for keyword in ALWAYS_CONFIRM_KEYWORDS:
            if keyword in haystack:
                log.warning(
                    "[copycat.browser] blocked tool=%r reason=keyword %r args=%s",
                    name,
                    keyword,
                    args,
                )
                return {
                    "error": (
                        f"This action ('{name}' on "
                        f"{args.get('element', args.get('target', '?'))}) "
                        f"looks like it involves '{keyword}', which wasn't "
                        "in the permissions approved for this skill. Stop "
                        "and report this instead of doing it."
                    )
                }

        log.info("[copycat.browser] allowing tool=%r args=%s", name, args)
        return None  # None = let the real tool call proceed

    return gate
