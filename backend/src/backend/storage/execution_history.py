from backend.database.supabase import supabase


def save_execution(
    command: str,
    skill_id: str,
    skill_name: str,
    environment: str,
    success: bool,
    execution_plan: dict,
    execution_result: dict,
):
    """
    Save an execution record to Supabase.
    """

    data = {
        "command": command,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "environment": environment,
        "success": success,
        "execution_plan": execution_plan,
        "execution_result": execution_result,
    }

    response = (
        supabase
        .table("execution_history")
        .insert(data)
        .execute()
    )

    return response.data[0]


def get_execution_history():
    """
    Retrieve execution history,
    newest first.
    """

    response = (
        supabase
        .table("execution_history")
        .select("*")
        .order(
            "created_at",
            desc=True,
        )
        .execute()
    )

    return response.data


def get_execution(
    execution_id: str,
):
    """
    Retrieve one execution record.
    """

    response = (
        supabase
        .table("execution_history")
        .select("*")
        .eq(
            "id",
            execution_id,
        )
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]