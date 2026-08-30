"""
Executes a browser execution plan.

Unlike the Windows executor, this doesn't walk `plan.steps` one by one -
DOM structure and element refs aren't known until the page actually loads,
so a rigid pre-scripted step list doesn't work here. Instead the plan's
`goal` (a synthesized natural-language task, see ai/planner.py) is handed to
an ADK agent that reasons live against the actual page.
"""

import asyncio
import time
from typing import Any

from google.adk.events.event import Event
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.genai import types

from backend.executors.browser_agent import build_browser_agent
from backend.logging_setup import log
from backend.models.execution import ExecutionPlan, ExecutionResult

_BROWSER_LOG = "copycat.browser"
_PROCESS_RECAP_MARKERS = (
    "i have successfully",
    "i successfully",
    "i have searched",
    "i searched your",
    "i then provided",
    "i then used",
    "using browser tools",
    "completed all sub-tasks",
    "sub-task 1",
)


def _summarize_args(args: dict[str, Any] | None) -> str:
    if not args:
        return "{}"
    parts: list[str] = []
    for key, value in args.items():
        text = repr(value)
        if len(text) > 100:
            text = text[:97] + "..."
        parts.append(f"{key}={text}")
    return "{" + ", ".join(parts) + "}"


def _log_browser_event(event: Event, *, event_index: int, elapsed_s: float) -> None:
    details: list[str] = []

    if event.author:
        details.append(f"author={event.author!r}")
    if event.error_message:
        details.append(f"error={event.error_message!r}")
    if event.finish_reason:
        details.append(f"finish={event.finish_reason}")
    if event.long_running_tool_ids:
        details.append(f"long_running={list(event.long_running_tool_ids)}")

    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.function_call:
                call = part.function_call
                details.append(
                    f"tool_call={call.name} args={_summarize_args(call.args)}"
                )
            elif part.function_response:
                response = part.function_response
                response_text = repr(response.response)
                if len(response_text) > 160:
                    response_text = response_text[:157] + "..."
                details.append(
                    f"tool_response={response.name} result={response_text}"
                )
            elif part.text:
                text = part.text.strip().replace("\n", " ")
                if len(text) > 120:
                    text = text[:117] + "..."
                details.append(f"text={text!r}")

    if not details:
        details.append("heartbeat")

    log.info(
        "[%s] event #%d at %.1fs: %s",
        _BROWSER_LOG,
        event_index,
        elapsed_s,
        " | ".join(details),
    )


def _is_process_recap(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in _PROCESS_RECAP_MARKERS)


def _extracted_from_event(event: Event) -> str:
    if not event.content or not event.content.parts:
        return ""
    for part in event.content.parts:
        call = part.function_call
        if call and call.name == "set_clipboard" and call.args:
            text = call.args.get("text")
            if isinstance(text, str) and len(text.strip()) > 40:
                return text.strip()
    return ""


class BrowserExecutionSession:
    """
    Reuses one Playwright MCP connection and ADK session across multiple
    browser plans in a single composition (avoids cold-starting npx per skill).
    """

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._runner: InMemoryRunner | None = None
        self._session_id: str | None = None
        self._browser_toolset: McpToolset | None = None
        self._mcp_connected = False
        self._needs_fresh_conversation = False

    def prewarm(self) -> None:
        log.info("[%s] prewarm requested", _BROWSER_LOG)
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(self._ensure_session())

    def execute_plan(
        self,
        plan: ExecutionPlan,
        *,
        new_conversation: bool = False,
    ) -> ExecutionResult:
        started = time.monotonic()
        if self._needs_fresh_conversation:
            new_conversation = True
            self._needs_fresh_conversation = False

        log.info(
            "[%s] execute_plan start skill=%r env=%s goal_len=%d new_conversation=%s",
            _BROWSER_LOG,
            plan.skill_name,
            plan.environment,
            len(plan.goal),
            new_conversation,
        )

        try:
            final_text = self._run_goal(plan.goal, new_conversation=new_conversation)
            elapsed_ms = (time.monotonic() - started) * 1000
            log.info(
                "[%s] execute_plan OK skill=%r in %.0fms",
                _BROWSER_LOG,
                plan.skill_name,
                elapsed_ms,
            )
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
            elapsed_ms = (time.monotonic() - started) * 1000
            log.exception(
                "[%s] execute_plan FAIL skill=%r after %.0fms: %s",
                _BROWSER_LOG,
                plan.skill_name,
                elapsed_ms,
                error,
            )
            return ExecutionResult(
                success=False,
                message=f"Browser execution failed: {str(error)}",
                skill_id=plan.skill_id,
                details={"goal": plan.goal},
            )

    def close(self) -> None:
        log.info("[%s] closing browser session (MCP subprocess will exit)", _BROWSER_LOG)
        if self._loop is not None:
            self._loop.close()
            self._loop = None
        self._runner = None
        self._session_id = None
        self._browser_toolset = None
        self._mcp_connected = False
        self._needs_fresh_conversation = False

    def _run_goal(self, goal: str, *, new_conversation: bool = False) -> str:
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        return self._loop.run_until_complete(
            self._run_goal_async(goal, new_conversation=new_conversation)
        )

    async def _connect_mcp_if_needed(self) -> None:
        if self._mcp_connected or self._browser_toolset is None:
            return

        connect_started = time.monotonic()
        log.info(
            "[%s] connecting Playwright MCP (npx spawn + browser launch)...",
            _BROWSER_LOG,
        )
        tools = await self._browser_toolset.get_tools()
        elapsed_ms = (time.monotonic() - connect_started) * 1000
        self._mcp_connected = True
        log.info(
            "[%s] Playwright MCP connected in %.0fms (%d tools available)",
            _BROWSER_LOG,
            elapsed_ms,
            len(tools),
        )

    async def _run_goal_async(
        self,
        goal: str,
        *,
        new_conversation: bool = False,
    ) -> str:
        run_started = time.monotonic()
        await self._ensure_session(new_conversation=new_conversation)
        setup_ms = (time.monotonic() - run_started) * 1000
        log.info(
            "[%s] setup complete in %.0fms (session_id=%s mcp_connected=%s)",
            _BROWSER_LOG,
            setup_ms,
            self._session_id,
            self._mcp_connected,
        )

        content = types.Content(role="user", parts=[types.Part(text=goal)])

        final_text = ""
        extracted_text = ""
        event_index = 0
        log.info("[%s] starting Gemini agent loop for goal...", _BROWSER_LOG)
        gemini_started = time.monotonic()

        async for event in self._runner.run_async(
            user_id="copycat_user",
            session_id=self._session_id,
            new_message=content,
        ):
            event_index += 1
            if event_index == 1:
                log.info(
                    "[%s] first agent event after %.0fms (Gemini + tool schema fetch)",
                    _BROWSER_LOG,
                    (time.monotonic() - gemini_started) * 1000,
                )
            _log_browser_event(
                event,
                event_index=event_index,
                elapsed_s=time.monotonic() - run_started,
            )
            captured = _extracted_from_event(event)
            if captured:
                extracted_text = captured
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text = part.text

        if extracted_text and (not final_text or _is_process_recap(final_text)):
            log.info("[%s] using extracted findings instead of process recap", _BROWSER_LOG)
            final_text = extracted_text

        total_ms = (time.monotonic() - run_started) * 1000
        log.info(
            "[%s] goal finished in %.0fms (%d events)",
            _BROWSER_LOG,
            total_ms,
            event_index,
        )
        return final_text

    async def _ensure_session(self, *, new_conversation: bool = False) -> None:
        session_started = time.monotonic()

        if self._runner is None:
            log.info("[%s] building ADK agent + Playwright MCP toolset", _BROWSER_LOG)
            agent, toolset = build_browser_agent()
            self._browser_toolset = toolset
            self._runner = InMemoryRunner(
                agent=agent,
                app_name="copycat_browser_execution",
            )
            log.info(
                "[%s] ADK runner created in %.0fms",
                _BROWSER_LOG,
                (time.monotonic() - session_started) * 1000,
            )
            await self._connect_mcp_if_needed()

        if self._session_id is None or new_conversation:
            if new_conversation and self._session_id is not None:
                log.info("[%s] starting fresh ADK conversation on existing MCP", _BROWSER_LOG)
            create_started = time.monotonic()
            session = await self._runner.session_service.create_session(
                app_name="copycat_browser_execution",
                user_id="copycat_user",
            )
            self._session_id = session.id
            log.info(
                "[%s] ADK conversation session created in %.0fms (session_id=%s)",
                _BROWSER_LOG,
                (time.monotonic() - create_started) * 1000,
                self._session_id,
            )


_prewarmed_session: BrowserExecutionSession | None = None
_idle_session: BrowserExecutionSession | None = None


def acquire_browser_session() -> BrowserExecutionSession:
    """Return a warm session when available, otherwise create a fresh one."""

    global _prewarmed_session, _idle_session

    if _prewarmed_session is not None:
        session = _prewarmed_session
        _prewarmed_session = None
        log.info("[%s] acquired prewarmed session (mcp_connected=%s)", _BROWSER_LOG, session._mcp_connected)
        return session

    if _idle_session is not None:
        session = _idle_session
        _idle_session = None
        session._needs_fresh_conversation = True
        log.info("[%s] acquired idle session (MCP reuse, fresh conversation)", _BROWSER_LOG)
        return session

    log.info("[%s] creating new browser session (MCP cold start)", _BROWSER_LOG)
    return BrowserExecutionSession()


def release_browser_session(session: BrowserExecutionSession) -> None:
    """Keep MCP alive for the next command instead of tearing it down."""

    global _idle_session

    if _idle_session is not None and _idle_session is not session:
        log.info("[%s] replacing previous idle session", _BROWSER_LOG)
        _idle_session.close()

    session._needs_fresh_conversation = True
    _idle_session = session
    log.info("[%s] session released to idle pool (MCP kept warm)", _BROWSER_LOG)


def prewarm_browser_session() -> None:
    """Start Playwright MCP early so the first command skips cold start."""

    global _prewarmed_session
    if _prewarmed_session is not None:
        log.info("[%s] prewarm skipped (already prewarmed)", _BROWSER_LOG)
        return
    session = BrowserExecutionSession()
    session.prewarm()
    _prewarmed_session = session
    log.info("[%s] prewarm complete (mcp_connected=%s)", _BROWSER_LOG, session._mcp_connected)


def execute_browser_plan(plan: ExecutionPlan) -> ExecutionResult:
    session = acquire_browser_session()
    try:
        return session.execute_plan(plan, new_conversation=True)
    finally:
        release_browser_session(session)
