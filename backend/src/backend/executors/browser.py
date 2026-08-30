"""
Executes a browser execution plan.

Unlike the Windows executor, this doesn't walk `plan.steps` one by one -
DOM structure and element refs aren't known until the page actually loads,
so a rigid pre-scripted step list doesn't work here. Instead the plan's
`goal` (a synthesized natural-language task, see ai/planner.py) is handed to
an ADK agent that reasons live against the actual page.
"""

import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from backend.executors.browser_agent import build_browser_agent
from backend.models.execution import ExecutionPlan, ExecutionResult


def execute_browser_plan(plan: ExecutionPlan) -> ExecutionResult:
    try:
        final_text = asyncio.run(_run_goal(plan.goal))

        return ExecutionResult(
            success=True,
            message=final_text or "Browser task completed.",
            skill_id=plan.skill_id,
            details={
                "goal": plan.goal,
                "demonstrated_steps": [
                    step.model_dump() for step in plan.steps
                ],
            },
        )

    except Exception as error:
        return ExecutionResult(
            success=False,
            message=f"Browser execution failed: {str(error)}",
            skill_id=plan.skill_id,
            details={"goal": plan.goal},
        )


async def _run_goal(goal: str) -> str:
    agent = build_browser_agent()

    runner = InMemoryRunner(agent=agent, app_name="copycat_browser_execution")
    session = await runner.session_service.create_session(
        app_name="copycat_browser_execution", user_id="copycat_user"
    )

    content = types.Content(role="user", parts=[types.Part(text=goal)])

    final_text = ""
    async for event in runner.run_async(
        user_id="copycat_user",
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text = part.text

    return final_text
