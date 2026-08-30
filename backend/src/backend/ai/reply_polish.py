"""Polish raw agent output into a short user-facing summary."""

from backend.ai.gemini_client import call_gemini
from backend.env_config import get_gemini_text_model


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

Write a concise reply (2-4 sentences) summarizing the outcome for the user.
- Focus on WHAT was found or done, not HOW (no step numbers, no sub-task labels).
- If there is an email summary, quote or paraphrase the key result.
- Do not mention skill names or internal workflow steps.
- Do not repeat the user's command back verbatim.

Return ONLY the summary text, no JSON.
"""

    try:
        response = call_gemini(
            model=get_gemini_text_model(),
            contents=prompt,
        )
        polished = (response.text or "").strip()
        return polished or _fallback_summary(raw_message)
    except Exception:
        return _fallback_summary(raw_message)


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
