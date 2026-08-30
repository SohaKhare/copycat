"""Polish raw agent output into a short user-facing summary."""

import time

from backend.ai.gemini_client import call_gemini
from backend.env_config import get_gemini_text_model
from backend.logging_setup import log


def polish_reply_text(
    *,
    command: str,
    raw_message: str,
    skill_names: list[str] | None = None,
) -> str:
    """
    Turn verbose agent output (sub-tasks, skill names, reasoning) into
    a concise outcome summary the user actually wants to read.
    """

    raw_message = raw_message.strip()
    if not raw_message:
        return "Done."

    skills_hint = ""
    if skill_names:
        skills_hint = f"Skills involved: {', '.join(skill_names)}.\n"

    prompt = f"""
The user asked CopyCat:
"{command}"

{skills_hint}
Raw execution output:
{raw_message}

Write the reply the user actually wants to read.
- If they asked for a summary, return the email/ChatGPT content itself
  (senders, subjects, offers, key facts) as a short numbered list.
- Never write process recap like "I searched", "I provided to ChatGPT",
  or "I successfully retrieved".
- Do not mention skill names or tool steps.
- Do not repeat the user's command back verbatim.

Return ONLY that content, no JSON.
"""

    # The browser agent already writes a user-facing summary. Another
    # Gemini round-trip was adding ~5s after the task was done.
    if _already_concise(raw_message):
        log.info("[copycat.pipeline] reply polish skipped (agent text already concise)")
        return raw_message

    try:
        polish_started = time.monotonic()
        response = call_gemini(
            model=get_gemini_text_model(),
            contents=prompt,
        )
        log.info(
            "[copycat.pipeline] reply polish finished in %.0fms",
            (time.monotonic() - polish_started) * 1000,
        )
        polished = (response.text or "").strip()
        return polished or _fallback_summary(raw_message)
    except Exception:
        return _fallback_summary(raw_message)


def _already_concise(raw_message: str) -> bool:
    lower = raw_message.lower()
    if "sub-task" in lower:
        return False
    if any(
        marker in lower
        for marker in (
            "i have successfully",
            "i successfully",
            "i have searched",
            "i then provided",
            "i then used",
        )
    ):
        return False
    if len(raw_message) > 700:
        return False
    return True


def _fallback_summary(raw_message: str) -> str:
    """Heuristic cleanup when Gemini polish is unavailable."""

    lines = [line.strip() for line in raw_message.splitlines() if line.strip()]
    kept: list[str] = []
    for line in lines:
        lower = line.lower()
        if lower.startswith("sub-task"):
            continue
        if lower.startswith("- sub-task"):
            continue
        if line[0].isdigit() and ". " in line[:4]:
            continue
        if lower.startswith("completed all steps"):
            continue
        kept.append(line)
    if kept:
        return " ".join(kept[-3:])
    return raw_message[:500]
