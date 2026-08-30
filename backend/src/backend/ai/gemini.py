import json
import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

from backend.ai.gemini_client import call_gemini
from backend.models.learning import LearningResult


load_dotenv()

ANALYSIS_MODEL = os.getenv("ANALYSIS_MODEL", "gemini-3.1-flash-lite")


def test_gemini():
    response = call_gemini(
        model=ANALYSIS_MODEL,
        contents="Say hello to CopyCat in one short sentence.",
    )

    return response.text


def analyze_frames(frames: list[dict]):
    """
    Analyze a screen-recorded demonstration and identify
    a reusable candidate skill with ordered execution steps.
    """

    prompt = """
You are analyzing a screen-recorded demonstration for CopyCat,
a voice-first personal assistant that learns digital skills by
watching a user perform them.

Your task is to understand what the user demonstrated and convert it
into a reusable digital skill.

You must distinguish clearly between:

1. OBSERVABLE FACTS
   Things directly visible in the demonstration.

2. INFERRED DECISIONS
   Possible reasons suggested by the user's actions.

3. CANDIDATE SKILL
   The main reusable task demonstrated.

4. SKILL STEPS
   The ordered actions needed to perform the demonstrated skill.

IMPORTANT RULES:

- Never present an inference as an observable fact.
- Only include actions supported by the video frames.
- Do not invent missing steps.
- Preserve the demonstrated order.
- Make action names concise and machine-readable.
- Put action-specific details inside observed_data.
- The skill must require user validation.
- Assign confidence based on how clearly the demonstration
  supports the identified skill.

Choose exactly one environment:

- browser
- windows

Use browser for any website or web-app task (Gmail, Drive, internal
dashboards, anything reachable through a browser).

Use windows for Windows desktop and file operations.

Return ONLY valid JSON.

Use exactly this structure:

{
  "goal": "string",

  "observations": [
    {
      "observable_fact": {
        "item": "string or null",
        "item_type": "string or null",
        "source_location": "string or null",
        "destination": "string or null"
      },

      "action": {
        "type": "string"
      },

      "inferred_decision": {
        "description": "string",
        "confidence": "low | medium | high"
      }
    }
  ],

  "candidate_skills": [
    {
      "name": "string",

      "description": "string",

      "environment": "browser | windows",

      "steps": [
        {
          "step_number": 1,
          "action": "machine_readable_action_name",
          "description": "string",
          "observed_data": {}
        }
      ],

      "confidence": "low | medium | high",

      "requires_user_validation": true,

      "status": "pending"
    }
  ]
}

Return one candidate skill for the main demonstrated task.
"""

    contents = [prompt]

    for frame_data in frames:
        image_path = Path(frame_data["path"])

        image = Image.open(image_path)

        contents.append(
            f"\nFrame timestamp: {frame_data['timestamp']} seconds"
        )

        contents.append(image)

    response = call_gemini(model=ANALYSIS_MODEL, contents=contents)

    cleaned_text = clean_json_response(response.text)

    result = json.loads(cleaned_text)

    return LearningResult(**result)


def analyze_description(description: str):
    """
    Turn a spoken or typed workflow description into the same candidate
    skill shape as a screen recording analysis.
    """

    prompt = f"""
You are creating a reusable digital skill for CopyCat from a user's
spoken or typed description of a workflow they want the assistant to
perform later.

USER DESCRIPTION:
\"\"\"{description}\"\"\"

Convert this into one candidate skill with ordered execution steps.

IMPORTANT RULES:

- Infer only what the description supports. Do not invent unrelated steps.
- Make action names concise and machine-readable.
- Put action-specific details (URLs, search terms, folder names) in observed_data.
- The skill must require user validation.
- Assign confidence based on how clearly the description specifies the task.

Choose exactly one environment:

- browser — any website or web-app task (Gmail, Drive, ChatGPT, dashboards)
- windows — Windows desktop and file operations

Return ONLY valid JSON.

Use exactly this structure:

{{
  "goal": "string",

  "observations": [
    {{
      "observable_fact": {{
        "item": "string or null",
        "item_type": "string or null",
        "source_location": "string or null",
        "destination": "string or null"
      }},

      "action": {{
        "type": "string"
      }},

      "inferred_decision": {{
        "description": "string",
        "confidence": "low | medium | high"
      }}
    }}
  ],

  "candidate_skills": [
    {{
      "name": "string",
      "description": "string",
      "environment": "browser | windows",
      "steps": [
        {{
          "step_number": 1,
          "action": "machine_readable_action_name",
          "description": "string",
          "observed_data": {{}}
        }}
      ],
      "confidence": "low | medium | high",
      "requires_user_validation": true,
      "status": "pending"
    }}
  ]
}}

Return one candidate skill for the main described task.
"""

    response = call_gemini(model=ANALYSIS_MODEL, contents=prompt)
    cleaned_text = clean_json_response(response.text or "")
    try:
        result = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "CopyCat couldn't turn that description into a skill. "
            "Try a clearer multi-step workflow."
        ) from error
    return LearningResult(**result)


def clean_json_response(text: str):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.startswith("```"):
        text = text.replace("```", "", 1)

    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return text.strip()
