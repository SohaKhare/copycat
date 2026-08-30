from pathlib import Path
import shutil

from backend.models.execution import (
    ExecutionPlan,
    ExecutionResult,
)


WORKSPACE = Path(
    r"D:\hackathons\gemini-hackdays\Workspace"
).resolve()


def get_safe_path(
    relative_path: str,
) -> Path:
    """
    Convert a relative workspace path into
    an absolute path.

    Reject paths outside the allowed workspace.
    """

    requested_path = (
        WORKSPACE / relative_path
    ).resolve()

    if requested_path != WORKSPACE:
        if WORKSPACE not in requested_path.parents:
            raise ValueError(
                "Operation outside the allowed "
                "workspace is not permitted."
            )

    return requested_path


def execute_windows_plan(
    plan: ExecutionPlan,
) -> ExecutionResult:
    """
    Execute a Windows execution plan.

    All operations are restricted to the
    CopyCat workspace.
    """

    step_results = []

    try:
        for step in plan.steps:

            result = execute_step(
                action=step.action,
                parameters=step.parameters,
            )

            step_results.append(
                {
                    "step_number": step.step_number,
                    "action": step.action,
                    "success": True,
                    "result": result,
                }
            )

        return ExecutionResult(
            success=True,
            message=(
                "Windows execution completed "
                "successfully."
            ),
            skill_id=plan.skill_id,
            details={
                "workspace": str(WORKSPACE),
                "steps": step_results,
            },
        )

    except Exception as error:

        return ExecutionResult(
            success=False,
            message=(
                f"Windows execution failed: "
                f"{str(error)}"
            ),
            skill_id=plan.skill_id,
            details={
                "workspace": str(WORKSPACE),
                "completed_steps": step_results,
            },
        )


def execute_step(
    action: str,
    parameters: dict,
):
    """
    Map a planned action to the appropriate
    Windows operation.
    """

    if action == "find_folder":
        return find_folder(
            parameters
        )

    if action == "find_file":
        return find_file(
            parameters
        )

    if action == "create_folder":
        return create_folder(
            parameters
        )

    if action == "rename_folder":
        return rename_folder(
            parameters
        )

    if action == "move_file":
        return move_file(
            parameters
        )

    if action == "verify_exists":
        return verify_exists(
            parameters
        )

    raise ValueError(
        f"Unsupported Windows action: {action}"
    )


def find_folder(
    parameters: dict,
):
    folder_path = parameters.get(
        "folder_path"
    )

    if not folder_path:
        raise ValueError(
            "folder_path is required."
        )

    path = get_safe_path(
        folder_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Folder not found: {folder_path}"
        )

    if not path.is_dir():
        raise ValueError(
            f"Path is not a folder: {folder_path}"
        )

    return {
        "found": True,
        "path": str(path),
    }


def find_file(
    parameters: dict,
):
    file_path = parameters.get(
        "file_path"
    )

    if not file_path:
        raise ValueError(
            "file_path is required."
        )

    path = get_safe_path(
        file_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    return {
        "found": True,
        "path": str(path),
    }


def create_folder(
    parameters: dict,
):
    folder_path = parameters.get(
        "folder_path"
    )

    if not folder_path:
        raise ValueError(
            "folder_path is required."
        )

    path = get_safe_path(
        folder_path
    )

    if path.exists():
        return {
            "created": False,
            "message": (
                "Folder already exists."
            ),
            "path": str(path),
        }

    path.mkdir(
        parents=True,
        exist_ok=False,
    )

    return {
        "created": True,
        "path": str(path),
    }


def rename_folder(
    parameters: dict,
):
    folder_path = parameters.get(
        "folder_path"
    )

    new_name = parameters.get(
        "new_name"
    )

    if not folder_path:
        raise ValueError(
            "folder_path is required."
        )

    if not new_name:
        raise ValueError(
            "new_name is required."
        )

    source_path = get_safe_path(
        folder_path
    )

    if not source_path.exists():
        raise FileNotFoundError(
            f"Folder not found: {folder_path}"
        )

    if not source_path.is_dir():
        raise ValueError(
            f"Path is not a folder: "
            f"{folder_path}"
        )

    destination_path = (
        source_path.parent / new_name
    ).resolve()

    if WORKSPACE not in destination_path.parents:
        raise ValueError(
            "Destination is outside the "
            "allowed workspace."
        )

    if destination_path.exists():
        raise FileExistsError(
            f"A folder named '{new_name}' "
            "already exists."
        )

    source_path.rename(
        destination_path
    )

    return {
        "renamed": True,
        "old_path": str(source_path),
        "new_path": str(destination_path),
    }


def move_file(
    parameters: dict,
):
    source_path_value = parameters.get(
        "source_path"
    )

    destination_folder_value = (
        parameters.get(
            "destination_folder"
        )
    )

    if not source_path_value:
        raise ValueError(
            "source_path is required."
        )

    if not destination_folder_value:
        raise ValueError(
            "destination_folder is required."
        )

    source_path = get_safe_path(
        source_path_value
    )

    destination_folder = get_safe_path(
        destination_folder_value
    )

    if not source_path.exists():
        raise FileNotFoundError(
            f"File not found: "
            f"{source_path_value}"
        )

    if not source_path.is_file():
        raise ValueError(
            f"Path is not a file: "
            f"{source_path_value}"
        )

    if not destination_folder.exists():
        raise FileNotFoundError(
            f"Destination folder not found: "
            f"{destination_folder_value}"
        )

    if not destination_folder.is_dir():
        raise ValueError(
            "Destination is not a folder."
        )

    destination_path = (
        destination_folder /
        source_path.name
    )

    if destination_path.exists():
        raise FileExistsError(
            "A file with the same name "
            "already exists in destination."
        )

    shutil.move(
        str(source_path),
        str(destination_path),
    )

    return {
        "moved": True,
        "source": str(source_path),
        "destination": str(
            destination_path
        ),
    }


def verify_exists(
    parameters: dict,
):
    path_value = parameters.get(
        "path"
    )

    if not path_value:
        raise ValueError(
            "path is required."
        )

    path = get_safe_path(
        path_value
    )

    exists = path.exists()

    if not exists:
        raise FileNotFoundError(
            f"Path does not exist: "
            f"{path_value}"
        )

    return {
        "exists": True,
        "path": str(path),
    }