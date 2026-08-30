import json
import os

from dotenv import load_dotenv

from backend.ai.gemini_client import call_gemini
from backend.models.execution import (
    ResolvedSkill,
    ResolvedSkillItem,
    ResolveSkillsResult,
    SkillParameter,
)


load_dotenv()

RESOLVER_MODEL = os.getenv("RESOLVER_MODEL", "gemini-3.1-flash-lite")


def resolve_skills(
    command: str,
    skills: list[dict],
) -> ResolveSkillsResult | None:
    """
    Determine which accepted skill(s) best match the user's command and
    extract relevant parameters, including multi-skill composition order.
    """

    by_id = {str(skill["id"]): skill for skill in skills if skill.get("id")}
    by_name = {
        str(skill.get("name", "")).lower(): skill
        for skill in skills
        if skill.get("name")
    }

    prompt = f"""
You are the Skill Resolver for CopyCat.

CopyCat is a personal AI assistant that learns digital skills from user
demonstrations.

The user has given this command:

"{command}"

Below are the ONLY skills CopyCat already knows (each has an exact `id`):

{json.dumps(_trim_skills_for_prompt(skills), indent=2)}

Your job:

1. Understand the user's command.
2. Select one or more skills from the list above that together fulfill the
   request, in the order they should run.
3. Extract parameter values from the command for each selected skill.
4. Copy the exact `id` field into `skill_id` in your response.
5. Do NOT invent a skill. Do NOT return a skill that is not in the list.
6. Prefer the most specific skill whose name/description matches the sub-task.
   Do not substitute a loosely related skill when a better match exists in
   the list.
7. If no skill is a reasonable match, return an empty skills array.
8. Prefer a single skill when the command only asks for one task.
9. Use multiple skills when the command clearly chains tasks with words like
   "then", "and then", "after that", or "and also".

Composition examples:

- "Search Gmail for internship emails then summarize the top one"
  -> order 1: search_gmail_by_keyword
  -> order 2: summarize_email_content
  Do NOT pick multi_engine_search unless the user explicitly asks to compare
  multiple AI engines or search the open web.

- "Organize these files by subject then open the semester folder"
  -> order 1: file-organize skill, order 2: open-folder skill

- "Query ChatGPT and copy the response"
  -> one skill: QueryAIChatbotAndCopyResponse only

- "Check my email"
  -> one matching email skill only; do not add unrelated skills

Return ONLY valid JSON.

Use exactly this structure:

{{
    "skills": [
        {{
            "skill_id": "exact id string copied from the list above",
            "skill_name": "string",
            "environment": "string",
            "parameters": [
                {{
                    "name": "string",
                    "value": "any value"
                }}
            ],
            "order": 1,
            "match_confidence": "low | medium | high"
        }}
    ],
    "reasoning": "short explanation of why these skills were chosen and their order"
}}
"""

    response = call_gemini(model=RESOLVER_MODEL, contents=prompt)

    cleaned_text = clean_json_response(response.text)
    result = json.loads(cleaned_text)

    raw_skills = result.get("skills") or []
    if not raw_skills and result.get("skill_id"):
        raw_skills = [result]

    reasoning = result.get("reasoning") or ""

    if not raw_skills:
        return None

    validated: list[ResolvedSkillItem] = []
    seen_orders: set[int] = set()
    seen_skill_ids: set[str] = set()

    for entry in raw_skills:
        if not isinstance(entry, dict):
            continue

        matched = _match_skill_record(entry, by_id, by_name)
        if matched is None:
            continue

        skill_id = str(matched["id"])
        if skill_id in seen_skill_ids:
            continue

        order = entry.get("order")
        if not isinstance(order, int) or order in seen_orders:
            order = len(validated) + 1

        seen_orders.add(order)
        seen_skill_ids.add(skill_id)
        validated.append(
            ResolvedSkillItem(
                skill_id=skill_id,
                skill_name=str(matched.get("name") or entry.get("skill_name") or ""),
                environment=str(
                    matched.get("environment") or entry.get("environment") or ""
                ),
                parameters=_normalize_parameters(entry.get("parameters")),
                order=order,
                match_confidence=str(entry.get("match_confidence") or "medium"),
            )
        )

    if not validated:
        return None

    validated.sort(key=lambda item: item.order)
    return ResolveSkillsResult(skills=validated, reasoning=reasoning)


def resolve_skill(
    command: str,
    skills: list[dict],
) -> ResolvedSkill | None:
    """Backward-compatible wrapper returning the first resolved skill."""

    resolution = resolve_skills(command, skills)
    if resolution is None or not resolution.skills:
        return None

    first = resolution.skills[0]
    return first.to_resolved_skill(reasoning=resolution.reasoning)


def _trim_skills_for_prompt(skills: list[dict]) -> list[dict]:
    return [
        {
            "id": skill.get("id"),
            "name": skill.get("name"),
            "description": skill.get("description"),
            "environment": skill.get("environment"),
            "steps": skill.get("steps"),
        }
        for skill in skills
    ]


def _match_skill_record(
    entry: dict,
    by_id: dict[str, dict],
    by_name: dict[str, dict],
) -> dict | None:
    skill_id = entry.get("skill_id")
    if skill_id is not None and str(skill_id) in by_id:
        return by_id[str(skill_id)]

    skill_name = entry.get("skill_name")
    if skill_name and str(skill_name).lower() in by_name:
        return by_name[str(skill_name).lower()]

    return None


def _normalize_parameters(raw_parameters) -> list[SkillParameter]:
    if not isinstance(raw_parameters, list):
        return []

    parameters: list[SkillParameter] = []
    for entry in raw_parameters:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if not name:
            continue
        parameters.append(
            SkillParameter(name=str(name), value=entry.get("value"))
        )
    return parameters


def clean_json_response(text: str):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.startswith("```"):
        text = text.replace("```", "", 1)

    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return text.strip()
