import json
import os

from dotenv import load_dotenv

from backend.ai.gemini_client import call_gemini
from backend.models.execution import (
    ExecutionPlan,
    ExecutionPlanStep,
    ResolvedSkill,
    ResolvedSkillItem,
    SkillParameter,
)


load_dotenv()

PLANNER_MODEL = os.getenv("PLANNER_MODEL", "gemini-3.1-flash-lite")


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

    response = call_gemini(model=PLANNER_MODEL, contents=prompt)

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


def build_compound_browser_plan(
    *,
    command: str,
    items: list[ResolvedSkillItem],
    skills_by_id: dict[str, dict],
) -> ExecutionPlan:
    """
    One browser goal for multiple sequential browser skills — single ADK session.
    """

    ordered_items = sorted(items, key=lambda item: item.order)
    subtask_lines: list[str] = []
    all_parameters: list[SkillParameter] = []
    all_steps: list[ExecutionPlanStep] = []
    step_offset = 0

    for index, item in enumerate(ordered_items, start=1):
        skill = skills_by_id[item.skill_id]
        parameter_lines = [
            f"{parameter.name}={parameter.value}" for parameter in item.parameters
        ]
        subtask_lines.append(
            f"Sub-task {index} — {item.skill_name}: "
            f"{skill.get('description') or 'No description'}"
            + (f" ({', '.join(parameter_lines)})" if parameter_lines else "")
        )
        all_parameters.extend(item.parameters)

        for step in skill.get("steps") or []:
            step_offset += 1
            all_steps.append(
                ExecutionPlanStep(
                    step_number=step_offset,
                    action=step.get("action", "demonstrated_step"),
                    description=(
                        f"[{item.skill_name}] "
                        f"{step.get('description') or step.get('action', '')}"
                    ),
                    parameters=step.get("observed_data") or {},
                )
            )

    combined_name = " -> ".join(item.skill_name for item in ordered_items)
    goal = (
        "Run these browser sub-tasks in order in ONE session. "
        "Do not restart the browser between sub-tasks.\n\n"
        + "\n".join(subtask_lines)
        + f'\n\nOverall user command: "{command}"\n\n'
        "Complete every sub-task above in order using browser tools. "
        "When finished, give a short summary with one line per sub-task."
    )

    return ExecutionPlan(
        skill_id=ordered_items[0].skill_id,
        skill_name=combined_name,
        environment="browser",
        goal=goal,
        parameters=all_parameters,
        steps=all_steps,
    )


def build_browser_subtask_plan(
    *,
    command: str,
    item: ResolvedSkillItem,
    skill: dict,
    continuation: bool = False,
) -> ExecutionPlan:
    """Lightweight per-skill plan for audit trails on merged browser runs."""

    resolved = item.to_resolved_skill()
    if not continuation:
        return _build_browser_plan(
            command=command,
            skill=skill,
            resolved_skill=resolved,
        )

    parameter_lines = [
        f"- {parameter.name}: {parameter.value}" for parameter in item.parameters
    ]
    goal_parts = [
        "Continue in the same browser session.",
        f"Sub-task: {item.skill_name} — {skill.get('description') or ''}",
    ]
    if parameter_lines:
        goal_parts.append("Parameters:\n" + "\n".join(parameter_lines))
    goal_parts.append(
        f'User command context: "{command}"\n'
        "Perform this sub-task now using browser tools."
    )

    return ExecutionPlan(
        skill_id=item.skill_id,
        skill_name=item.skill_name,
        environment=item.environment,
        goal="\n\n".join(goal_parts),
        parameters=item.parameters,
        steps=[
            ExecutionPlanStep(
                step_number=step.get("step_number", index + 1),
                action=step.get("action", "demonstrated_step"),
                description=step.get("description", ""),
                parameters=step.get("observed_data") or {},
            )
            for index, step in enumerate(skill.get("steps") or [])
        ],
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
