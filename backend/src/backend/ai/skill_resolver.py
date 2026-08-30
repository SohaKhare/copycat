import json
import os

from dotenv import load_dotenv

from backend.ai.gemini_client import call_gemini
from backend.models.execution import ResolvedSkill


load_dotenv()

RESOLVER_MODEL = os.getenv("RESOLVER_MODEL", "gemini-3.1-flash-lite")


def resolve_skill(
    command: str,
    skills: list[dict],
):
    """
    Determine which accepted skill best matches
    the user's command and extract relevant parameters.
    """

    prompt = f"""
You are the Skill Resolver for CopyCat.

CopyCat is a personal AI assistant that learns
digital skills from user demonstrations.

The user has given this command:

"{command}"

Below are the skills CopyCat already knows:

{json.dumps(skills, indent=2)}

Your job:

1. Understand the user's command.
2. Find the single best matching skill.
3. Extract values from the user's command that can
   be used as parameters for that skill.
4. Do NOT invent a skill.
5. Only select a skill from the provided list.
6. If no skill is a reasonable match, return null
   for skill_id and skill_name.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "skill_id": "string or null",

    "skill_name": "string or null",

    "environment": "string or null",

    "parameters": [
        {{
            "name": "string",
            "value": "any value"
        }}
    ],

    "match_confidence": "low | medium | high",

    "reasoning": "short explanation"
}}
"""

    response = call_gemini(model=RESOLVER_MODEL, contents=prompt)

    cleaned_text = clean_json_response(
        response.text
    )

    result = json.loads(cleaned_text)

    if result.get("skill_id") is None:
        return None

    return ResolvedSkill(**result)


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