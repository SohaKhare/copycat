import json
import os

from dotenv import load_dotenv
from google import genai

from backend.ai.retry import gemini_retry
from backend.models.execution import (
    ExecutionPlan,
    ExecutionPlanStep,
    ResolvedSkill,
)


load_dotenv()


WORKSPACE_PATH = (
    r"D:\hackathons\gemini-hackdays\Workspace"
)


def create_execution_plan(
    command: str,
    skill: dict,
    resolved_skill: ResolvedSkill,
):
    """
    Create a concrete execution plan for the
    user's specific request.
    """

    environment = resolved_skill.environment.lower()

    if environment == "browser":
        # Browser plans skip the Gemini planning call entirely: DOM
        # structure and element refs aren't known until the page actually
        # loads, so there's nothing useful to pre-plan. The browser
        # executor's own agent does the real step-by-step reasoning live
        # against the page - this just assembles the goal text it acts on.
        return _build_browser_plan(
            command=command,
            skill=skill,
            resolved_skill=resolved_skill,
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found in the environment."
        )

    client = genai.Client(
        api_key=api_key
    )

    resolved_skill_data = (
        resolved_skill.model_dump()
    )

    prompt = f"""
You are the Execution Planner for CopyCat.

CopyCat is a personal AI assistant that learns
digital tasks from user demonstrations.

Your job is to create a concrete execution plan.

USER COMMAND:

"{command}"

MATCHED SKILL:

{json.dumps(skill, indent=2)}

RESOLVED PARAMETERS:

{json.dumps(resolved_skill_data, indent=2)}

EXECUTION WORKSPACE:

{WORKSPACE_PATH}

IMPORTANT SAFETY RULE:

CopyCat is ONLY allowed to operate inside the
execution workspace shown above.

Do NOT generate operations outside that workspace.

For OS skills, you may ONLY use these actions:

1. find_folder
2. find_file
3. create_folder
4. rename_folder
5. move_file
6. verify_exists

DO NOT invent other action names.

PARAMETER REQUIREMENTS:

find_folder:
{{
    "folder_path": "relative path inside workspace"
}}

find_file:
{{
    "file_path": "relative path inside workspace"
}}

create_folder:
{{
    "folder_path": "relative path to create"
}}

rename_folder:
{{
    "folder_path": "current relative folder path",
    "new_name": "new folder name"
}}

move_file:
{{
    "source_path": "relative file path",
    "destination_folder": "relative destination folder path"
}}

verify_exists:
{{
    "path": "relative path inside workspace"
}}

IMPORTANT:

- All paths must be RELATIVE to the workspace.
- Never include the full workspace path in parameters.
- Adapt the learned skill to the user's current request.
- Do not invent unrelated actions.
- Include verification when appropriate.
- Preserve the matched skill's environment.
- Do not perform the task.
- Only generate the execution plan.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "skill_id": "string",
    "skill_name": "string",
    "environment": "string",
    "goal": "string",

    "parameters": [
        {{
            "name": "string",
            "value": "any"
        }}
    ],

    "steps": [
        {{
            "step_number": 1,
            "action": "one supported action",
            "description": "string",
            "parameters": {{
                "key": "value"
            }}
        }}
    ]
}}
"""

    response = (
        gemini_retry(client.models.generate_content)(
            model="gemini-3.1-flash-lite",
            contents=prompt,
        )
    )

    cleaned_text = clean_json_response(
        response.text
    )

    result = json.loads(
        cleaned_text
    )

    return ExecutionPlan(
        **result
    )


def _build_browser_plan(
    command: str,
    skill: dict,
    resolved_skill: ResolvedSkill,
) -> ExecutionPlan:
    """
    Assemble a browser execution plan without an extra Gemini call.

    `goal` is the natural-language task the browser executor's agent will
    reason over live; `steps` are the originally demonstrated steps, carried
    through unmodified as an audit trail (not meant to be replayed literally
    step-by-step - the agent re-derives the actual clicks against whatever
    the page looks like at execution time).
    """

    demonstrated_steps = skill.get("steps") or []

    step_lines = [
        f"{step.get('step_number', index + 1)}. "
        f"{step.get('description') or step.get('action', '')}"
        for index, step in enumerate(demonstrated_steps)
    ]

    parameter_lines = [
        f"- {parameter.name}: {parameter.value}"
        for parameter in resolved_skill.parameters
    ]

    goal_parts = [
        f"Learned skill: {skill.get('name')} - {skill.get('description')}",
        "Demonstrated steps:\n" + "\n".join(step_lines),
    ]

    if parameter_lines:
        goal_parts.append(
            "Parameters for this run:\n" + "\n".join(parameter_lines)
        )

    goal_parts.append(
        f'Current user request: "{command}"\n\n'
        "Combine the demonstrated steps above with the current request - "
        "the request can add exceptions or narrow the skill, but don't "
        "ignore the base workflow. Use the browser tools to actually "
        "perform this, don't just describe it."
    )

    goal = "\n\n".join(goal_parts)

    plan_steps = [
        ExecutionPlanStep(
            step_number=step.get("step_number", index + 1),
            action=step.get("action", "demonstrated_step"),
            description=step.get("description", ""),
            parameters=step.get("observed_data") or {},
        )
        for index, step in enumerate(demonstrated_steps)
    ]

    return ExecutionPlan(
        skill_id=resolved_skill.skill_id,
        skill_name=resolved_skill.skill_name,
        environment=resolved_skill.environment,
        goal=goal,
        parameters=resolved_skill.parameters,
        steps=plan_steps,
    )


def clean_json_response(text: str):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace(
            "```json",
            "",
            1,
        )

    if text.startswith("```"):
        text = text.replace(
            "```",
            "",
            1,
        )

    if text.endswith("```"):
        text = text.rsplit(
            "```",
            1,
        )[0]

    return text.strip()