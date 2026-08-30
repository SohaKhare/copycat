"""
Bridges a transcribed voice command into the real skill pipeline - the same
resolve -> plan -> execute -> log chain the POST /execute HTTP endpoint uses,
so a voice-triggered request isn't a separate, ad-hoc execution path.
"""

from backend.ai.planner import create_execution_plan
from backend.ai.skill_resolver import resolve_skill
from backend.executors.router import execute_plan
from backend.storage.execution_history import save_execution
from backend.storage.skills import get_accepted_skills, get_skill


def run_command(command: str) -> str:
    """
    Runs `command` through the same pipeline as POST /execute, and returns a
    short spoken-style summary of the outcome.

    Blocking/synchronous - the browser executor spins up its own event loop
    internally, so call this via asyncio.to_thread from async contexts
    (like the voice session), never directly inside a running event loop.
    """

    accepted_skills = get_accepted_skills()

    if not accepted_skills:
        return (
            "You haven't taught me anything yet - "
            "there are no accepted skills."
        )

    resolved_skill = resolve_skill(
        command=command,
        skills=accepted_skills,
    )

    if resolved_skill is None:
        return "I don't have a skill that matches that request yet."

    skill = get_skill(resolved_skill.skill_id)

    if skill is None:
        return "I found a matching skill, but couldn't load its details."

    execution_plan = create_execution_plan(
        command=command,
        skill=skill,
        resolved_skill=resolved_skill,
    )

    execution_result = execute_plan(execution_plan)

    save_execution(
        command=command,
        skill_id=resolved_skill.skill_id,
        skill_name=resolved_skill.skill_name,
        environment=resolved_skill.environment,
        success=execution_result.success,
        execution_plan=execution_plan.model_dump(),
        execution_result=execution_result.model_dump(),
    )

    return execution_result.message
