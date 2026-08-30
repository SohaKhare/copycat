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


class BrowserExecutionSession:
    """
    Reuses one Playwright MCP connection and ADK session across multiple
    browser plans in a single composition (avoids cold-starting npx per skill).
    """

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._runner: InMemoryRunner | None = None
        self._session_id: str | None = None

    def prewarm(self) -> None:
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(self._ensure_session())

    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        try:
            final_text = self._run_goal(plan.goal)
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

    def close(self) -> None:
        if self._loop is not None:
            self._loop.close()
            self._loop = None
        self._runner = None
        self._session_id = None

    def _run_goal(self, goal: str) -> str:
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        return self._loop.run_until_complete(self._run_goal_async(goal))

    async def _run_goal_async(self, goal: str) -> str:
        await self._ensure_session()

        content = types.Content(role="user", parts=[types.Part(text=goal)])

        final_text = ""
        async for event in self._runner.run_async(
            user_id="copycat_user",
            session_id=self._session_id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text = part.text

        return final_text

    async def _ensure_session(self) -> None:
        if self._runner is not None and self._session_id is not None:
            return

        agent = build_browser_agent()
        self._runner = InMemoryRunner(
            agent=agent,
            app_name="copycat_browser_execution",
        )
        session = await self._runner.session_service.create_session(
            app_name="copycat_browser_execution",
            user_id="copycat_user",
        )
        self._session_id = session.id


_prewarmed_session: BrowserExecutionSession | None = None


def acquire_browser_session() -> BrowserExecutionSession:
    """Return a pre-warmed session if available, otherwise a fresh one."""

    global _prewarmed_session
    if _prewarmed_session is not None:
        session = _prewarmed_session
        _prewarmed_session = None
        return session
    return BrowserExecutionSession()


def prewarm_browser_session() -> None:
    """Start Playwright MCP early so the first command skips cold start."""

    global _prewarmed_session
    if _prewarmed_session is not None:
        return
    session = BrowserExecutionSession()
    session.prewarm()
    _prewarmed_session = session


def execute_browser_plan(plan: ExecutionPlan) -> ExecutionResult:
    session = acquire_browser_session()
    try:
        return session.execute_plan(plan)
    finally:
        session.close()
