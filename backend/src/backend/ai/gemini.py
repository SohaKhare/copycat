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


def clean_json_response(text: str):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.startswith("```"):
        text = text.replace("```", "", 1)

    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return text.strip()