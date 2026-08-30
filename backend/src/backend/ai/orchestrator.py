"""Sequential multi-skill orchestration: plan, execute, and merge results."""

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from backend.ai.planner import (
    build_browser_subtask_plan,
    build_compound_browser_plan,
    create_execution_plan,
)
from backend.ai.user_reply import Modality, UserReply, build_multi_skill_reply
from backend.executors.browser import (
    BrowserExecutionSession,
    acquire_browser_session,
    release_browser_session,
)
from backend.executors.router import execute_plan
from backend.logging_setup import log
from backend.models.execution import (
    ExecutionPlan,
    ExecutionResult,
    ResolveSkillsResult,
    ResolvedSkillItem,
    SkillRunResult,
)
from backend.storage.execution_history import save_execution


@dataclass
class OrchestrationResult:
    runs: list[SkillRunResult]
    reply: UserReply
    stopped_at_order: int | None = None


@dataclass
class _PlannedSkill:
    item: ResolvedSkillItem
    skill: dict
    execution_plan: ExecutionPlan


def orchestrate_skills(
    *,
    command: str,
    resolution: ResolveSkillsResult,
    modality: Modality,
    skills_by_id: dict[str, dict] | None = None,
) -> OrchestrationResult:
    skills_by_id = skills_by_id or {}
    runs: list[SkillRunResult] = []
    stopped_at_order: int | None = None

    ordered_items = sorted(resolution.skills, key=lambda item: item.order)
    for item in ordered_items:
        if item.skill_id not in skills_by_id:
            runs.append(skill_not_loaded_run(item))
            stopped_at_order = item.order
            return OrchestrationResult(
                runs=runs,
                reply=build_multi_skill_reply(
                    command=command,
                    modality=modality,
                    runs=runs,
                    reasoning=resolution.reasoning,
                    stopped_at_order=stopped_at_order,
                ),
                stopped_at_order=stopped_at_order,
            )

    needs_browser = any(
        item.environment.lower() == "browser" for item in ordered_items
    )
    browser_session: BrowserExecutionSession | None = None
    orchestration_started = time.monotonic()

    try:
        if needs_browser:
            browser_session = acquire_browser_session()

        if _should_merge_browser_skills(ordered_items):
            runs, stopped_at_order = _execute_merged_browser_skills(
                command=command,
                ordered_items=ordered_items,
                skills_by_id=skills_by_id,
                browser_session=browser_session,
            )
        else:
            runs, stopped_at_order = _execute_sequential_skills(
                command=command,
                resolution=resolution,
                ordered_items=ordered_items,
                skills_by_id=skills_by_id,
                browser_session=browser_session,
            )
    finally:
        if browser_session is not None:
            release_browser_session(browser_session)

    log.info(
        "[copycat.orchestrator] finished in %.0fms (browser=%s skills=%d)",
        (time.monotonic() - orchestration_started) * 1000,
        needs_browser,
        len(ordered_items),
    )

    reply = build_multi_skill_reply(
        command=command,
        modality=modality,
        runs=runs,
        reasoning=resolution.reasoning,
        stopped_at_order=stopped_at_order,
    )

    return OrchestrationResult(
        runs=runs,
        reply=reply,
        stopped_at_order=stopped_at_order,
    )


def _should_merge_browser_skills(items: list[ResolvedSkillItem]) -> bool:
    return len(items) > 1 and all(
        item.environment.lower() == "browser" for item in items
    )


def _execute_merged_browser_skills(
    *,
    command: str,
    ordered_items: list[ResolvedSkillItem],
    skills_by_id: dict[str, dict],
    browser_session: BrowserExecutionSession | None,
) -> tuple[list[SkillRunResult], int | None]:
    if browser_session is None:
        raise RuntimeError("Merged browser skills require a browser session.")

    compound_plan = build_compound_browser_plan(
        command=command,
        items=ordered_items,
        skills_by_id=skills_by_id,
    )
    compound_result = browser_session.execute_plan(compound_plan)

    runs: list[SkillRunResult] = []
    stopped_at_order: int | None = None

    for index, item in enumerate(ordered_items):
        audit_plan = build_browser_subtask_plan(
            command=command,
            item=item,
            skill=skills_by_id[item.skill_id],
            continuation=index > 0,
        )
        per_skill_result = ExecutionResult(
            success=compound_result.success,
            message=compound_result.message,
            skill_id=item.skill_id,
            details={
                **compound_result.details,
                "merged_run": True,
                "compound_skill_name": compound_plan.skill_name,
            },
        )
        saved_execution = save_execution(
            command=command,
            skill_id=item.skill_id,
            skill_name=item.skill_name,
            environment=item.environment,
            success=compound_result.success,
            execution_plan=audit_plan.model_dump(),
            execution_result=per_skill_result.model_dump(),
        )
        runs.append(
            SkillRunResult(
                order=item.order,
                skill_id=item.skill_id,
                skill_name=item.skill_name,
                environment=item.environment,
                success=compound_result.success,
                message=compound_result.message,
                execution_plan=audit_plan,
                execution_result=per_skill_result,
                execution_history=saved_execution,
            )
        )

    if not compound_result.success:
        stopped_at_order = ordered_items[-1].order

    return runs, stopped_at_order


def _execute_sequential_skills(
    *,
    command: str,
    resolution: ResolveSkillsResult,
    ordered_items: list[ResolvedSkillItem],
    skills_by_id: dict[str, dict],
    browser_session: BrowserExecutionSession | None,
) -> tuple[list[SkillRunResult], int | None]:
    runs: list[SkillRunResult] = []
    stopped_at_order: int | None = None

    planned = _plan_all_skills(
        command=command,
        resolution=resolution,
        skills_by_id=skills_by_id,
    )

    for planned_skill in planned:
        item = planned_skill.item
        execution_plan = planned_skill.execution_plan

        if item.environment.lower() == "browser":
            if browser_session is None:
                raise RuntimeError("Browser skill requires a browser session.")
            skill_started = time.monotonic()
            execution_result = browser_session.execute_plan(execution_plan)
            log.info(
                "[copycat.orchestrator] browser skill=%r finished in %.0fms success=%s",
                item.skill_name,
                (time.monotonic() - skill_started) * 1000,
                execution_result.success,
            )
        else:
            execution_result = execute_plan(execution_plan)

        saved_execution = save_execution(
            command=command,
            skill_id=item.skill_id,
            skill_name=item.skill_name,
            environment=item.environment,
            success=execution_result.success,
            execution_plan=execution_plan.model_dump(),
            execution_result=execution_result.model_dump(),
        )

        runs.append(
            SkillRunResult(
                order=item.order,
                skill_id=item.skill_id,
                skill_name=item.skill_name,
                environment=item.environment,
                success=execution_result.success,
                message=execution_result.message,
                execution_plan=execution_plan,
                execution_result=execution_result,
                execution_history=saved_execution,
            )
        )

        if not execution_result.success:
            stopped_at_order = item.order
            break

    return runs, stopped_at_order


def _plan_all_skills(
    *,
    command: str,
    resolution: ResolveSkillsResult,
    skills_by_id: dict[str, dict],
) -> list[_PlannedSkill]:
    ordered_items = sorted(resolution.skills, key=lambda item: item.order)
    planned: list[_PlannedSkill | None] = [None] * len(ordered_items)

    def _plan_one(index: int, item: ResolvedSkillItem) -> _PlannedSkill:
        skill = skills_by_id[item.skill_id]
        resolved_skill = item.to_resolved_skill(reasoning=resolution.reasoning)
        execution_plan = create_execution_plan(
            command=command,
            skill=skill,
            resolved_skill=resolved_skill,
        )
        return _PlannedSkill(
            item=item,
            skill=skill,
            execution_plan=execution_plan,
        )

    windows_indexes = [
        index
        for index, item in enumerate(ordered_items)
        if item.environment.lower() != "browser"
    ]

    if len(windows_indexes) > 1:
        with ThreadPoolExecutor(max_workers=min(len(windows_indexes), 4)) as pool:
            futures = {
                pool.submit(_plan_one, index, ordered_items[index]): index
                for index in windows_indexes
            }
            for future in futures:
                index = futures[future]
                planned[index] = future.result()
    elif len(windows_indexes) == 1:
        index = windows_indexes[0]
        planned[index] = _plan_one(index, ordered_items[index])

    result: list[_PlannedSkill] = []
    for index, item in enumerate(ordered_items):
        if planned[index] is not None:
            result.append(planned[index])
            continue

        skill = skills_by_id[item.skill_id]
        resolved_skill = item.to_resolved_skill(reasoning=resolution.reasoning)
        result.append(
            _PlannedSkill(
                item=item,
                skill=skill,
                execution_plan=create_execution_plan(
                    command=command,
                    skill=skill,
                    resolved_skill=resolved_skill,
                ),
            )
        )

    return result


def skill_not_loaded_run(item: ResolvedSkillItem) -> SkillRunResult:
    empty_plan = ExecutionPlan(
        skill_id=item.skill_id,
        skill_name=item.skill_name,
        environment=item.environment,
        goal="",
        parameters=item.parameters,
        steps=[],
    )
    return SkillRunResult(
        order=item.order,
        skill_id=item.skill_id,
        skill_name=item.skill_name or item.skill_id,
        environment=item.environment,
        success=False,
        message="Skill could not be loaded.",
        execution_plan=empty_plan,
        execution_result=ExecutionResult(
            success=False,
            message="Skill could not be loaded.",
            skill_id=item.skill_id,
        ),
    )
