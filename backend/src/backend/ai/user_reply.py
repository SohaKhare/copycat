"""User-facing reply contract: text, speakable, modality."""

from typing import Literal

from pydantic import BaseModel

from backend.ai.reply_polish import polish_reply_text
from backend.models.execution import ExecutionResult, ResolvedSkill, SkillRunResult


Modality = Literal["text", "voice"]


class UserReply(BaseModel):
    text: str
    speakable: str
    modality: Modality


def build_user_reply(
    *,
    command: str,
    modality: Modality,
    resolved_skill: ResolvedSkill | None = None,
    execution_result: ExecutionResult | None = None,
    no_skills: bool = False,
) -> UserReply:
    if no_skills:
        return UserReply(
            text=(
                "You haven't taught CopyCat any skills yet. Record a "
                "demonstration, accept a skill, then try again."
            ),
            speakable="You haven't taught me anything yet.",
            modality=modality,
        )

    if resolved_skill is None:
        return UserReply(
            text=(
                f'No matching skill found for "{command}". Teach CopyCat the '
                "workflow, accept the skill, then try again with similar wording."
            ),
            speakable="I don't have a skill that matches that request yet.",
            modality=modality,
        )

    skill_name = resolved_skill.skill_name
    success = execution_result.success if execution_result else False
    raw_detail = execution_result.message if execution_result else ""

    if success:
        text = polish_reply_text(
            command=command,
            raw_message=raw_detail,
            skill_names=[skill_name],
        )
        speakable = _short_speakable(text)
    else:
        text = f"Sorry, that didn't work. {raw_detail}".strip()
        speakable = f"Sorry, {skill_name} didn't work."

    return UserReply(
        text=text,
        speakable=speakable,
        modality=modality,
    )


def build_multi_skill_reply(
    *,
    command: str,
    modality: Modality,
    runs: list[SkillRunResult],
    reasoning: str = "",
    stopped_at_order: int | None = None,
) -> UserReply:
    if not runs:
        return build_user_reply(
            command=command,
            modality=modality,
        )

    if len(runs) == 1:
        run = runs[0]
        return build_user_reply(
            command=command,
            modality=modality,
            resolved_skill=_run_as_resolved_skill(run, reasoning),
            execution_result=run.execution_result,
        )

    skill_names = [run.skill_name for run in runs]
    raw_message = runs[-1].message if runs else ""

    if stopped_at_order is None and all(run.success for run in runs):
        text = polish_reply_text(
            command=command,
            raw_message=raw_message,
            skill_names=skill_names,
        )
        speakable = _short_speakable(text)
    else:
        failed = next((run for run in runs if not run.success), None)
        if failed:
            completed = [run.skill_name for run in runs if run.success]
            if completed:
                text = (
                    f"Stopped at {failed.skill_name}. "
                    f"Completed: {', '.join(completed)}. {failed.message}"
                )
            else:
                text = f"{failed.skill_name} failed. {failed.message}"
            speakable = f"Stopped at {failed.skill_name}. It didn't work."
        else:
            text = polish_reply_text(
                command=command,
                raw_message=raw_message,
                skill_names=skill_names,
            )
            speakable = _short_speakable(text)

    return UserReply(
        text=text.strip(),
        speakable=speakable,
        modality=modality,
    )


def _short_speakable(text: str, max_len: int = 120) -> str:
    first_sentence = text.split(".")[0].strip()
    if not first_sentence:
        return "Done."
    if len(first_sentence) <= max_len:
        return f"{first_sentence}."
    return f"{first_sentence[: max_len - 3].rstrip()}..."


def _run_as_resolved_skill(
    run: SkillRunResult,
    reasoning: str,
) -> ResolvedSkill:
    return ResolvedSkill(
        skill_id=run.skill_id,
        skill_name=run.skill_name,
        environment=run.environment,
        parameters=run.execution_plan.parameters,
        match_confidence="medium",
        reasoning=reasoning,
    )
