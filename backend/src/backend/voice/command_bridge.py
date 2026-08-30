"""
Bridges a transcribed voice command into the real skill pipeline - the same
resolve -> plan -> execute -> log chain the POST /execute HTTP endpoint uses,
so a voice-triggered request isn't a separate, ad-hoc execution path.
"""

import time
from dataclasses import dataclass

from backend.ai.orchestrator import orchestrate_skills
from backend.ai.skill_resolver import resolve_skills
from backend.ai.user_reply import Modality, UserReply, build_user_reply
from backend.logging_setup import log
from backend.models.execution import (
    ExecutionPlan,
    ExecutionResult,
    ResolvedSkill,
    ResolvedSkillItem,
    SkillRunResult,
)
from backend.storage.skills import get_accepted_skills


@dataclass
class CommandPipelineResult:
    resolved_skills: list[ResolvedSkillItem]
    reasoning: str
    skill_runs: list[SkillRunResult]
    resolved_skill: ResolvedSkill | None
    execution_plan: ExecutionPlan | None
    execution_result: ExecutionResult | None
    execution_history: dict | None
    reply: UserReply
    stopped_at_order: int | None = None


def run_command(
    command: str,
    modality: Modality = "voice",
) -> CommandPipelineResult:
    """
    Runs `command` through the same pipeline as POST /execute.

    Blocking/synchronous - the browser executor spins up its own event loop
    internally, so call this via asyncio.to_thread from async contexts
    (like the voice session), never directly inside a running event loop.
    """

    accepted_skills = get_accepted_skills()

    if not accepted_skills:
        reply = build_user_reply(
            command=command,
            modality=modality,
            no_skills=True,
        )
        return _empty_result(reply)

    pipeline_started = time.monotonic()

    resolve_started = time.monotonic()
    resolution = resolve_skills(
        command=command,
        skills=accepted_skills,
    )
    resolve_ms = (time.monotonic() - resolve_started) * 1000

    if resolution is None or not resolution.skills:
        log.info(
            "[copycat.pipeline] resolve finished in %.0fms (no match) total=%.0fms",
            resolve_ms,
            (time.monotonic() - pipeline_started) * 1000,
        )
        reply = build_user_reply(
            command=command,
            modality=modality,
        )
        return _empty_result(reply)

    skills_by_id = {
        skill["id"]: skill for skill in accepted_skills if skill.get("id")
    }

    orchestrate_started = time.monotonic()
    orchestration = orchestrate_skills(
        command=command,
        resolution=resolution,
        modality=modality,
        skills_by_id=skills_by_id,
    )
    orchestrate_ms = (time.monotonic() - orchestrate_started) * 1000
    total_ms = (time.monotonic() - pipeline_started) * 1000

    environments = [item.environment for item in resolution.skills]
    log.info(
        "[copycat.pipeline] resolve=%.0fms orchestrate=%.0fms total=%.0fms "
        "skills=%d envs=%s",
        resolve_ms,
        orchestrate_ms,
        total_ms,
        len(resolution.skills),
        environments,
    )

    first_run = orchestration.runs[0] if orchestration.runs else None
    last_run = orchestration.runs[-1] if orchestration.runs else None

    resolved_skill = (
        resolution.skills[0].to_resolved_skill(reasoning=resolution.reasoning)
        if resolution.skills
        else None
    )

    return CommandPipelineResult(
        resolved_skills=resolution.skills,
        reasoning=resolution.reasoning,
        skill_runs=orchestration.runs,
        resolved_skill=resolved_skill,
        execution_plan=first_run.execution_plan if first_run else None,
        execution_result=last_run.execution_result if last_run else None,
        execution_history=last_run.execution_history if last_run else None,
        reply=orchestration.reply,
        stopped_at_order=orchestration.stopped_at_order,
    )


def _empty_result(reply: UserReply) -> CommandPipelineResult:
    return CommandPipelineResult(
        resolved_skills=[],
        reasoning="",
        skill_runs=[],
        resolved_skill=None,
        execution_plan=None,
        execution_result=None,
        execution_history=None,
        reply=reply,
    )
