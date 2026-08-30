from backend.executors.browser import (
    execute_browser_plan,
)

from backend.executors.windows import (
    execute_windows_plan,
)

from backend.models.execution import (
    ExecutionPlan,
    ExecutionResult,
)

from backend.executors.system import (
    get_current_environment,
)


from backend.executors.macos import (
    execute_macos_plan,
)

def execute_plan(
    plan: ExecutionPlan,
) -> ExecutionResult:
    """
    Send an execution plan to the appropriate
    environment executor.

    The skill environment must match the
    operating system where CopyCat is running.
    """

    required_environment = (
        plan.environment.lower()
    )

    current_environment = (
        get_current_environment()
    )

    # "browser" skills run inside Playwright's own Chromium, portable
    # across any host OS - only OS-native skills (windows/macos) need to
    # match the machine CopyCat is actually running on.
    if (
        required_environment != "browser"
        and required_environment != current_environment
    ):
        return ExecutionResult(
            success=False,
            message=(
                f"This skill requires "
                f"{required_environment}, "
                f"but CopyCat is currently "
                f"running on "
                f"{current_environment}."
            ),
            skill_id=plan.skill_id,
            details={
                "required_environment":
                    required_environment,
                "current_environment":
                    current_environment,
            },
        )

    if required_environment == "windows":
        return execute_windows_plan(
            plan
        )

    if required_environment == "browser":
        return execute_browser_plan(
            plan
        )

    if required_environment == "macos":
        return execute_macos_plan(
            plan
        )

    raise ValueError(
        f"No executor is available for "
        f"environment: "
        f"{required_environment}"
    )