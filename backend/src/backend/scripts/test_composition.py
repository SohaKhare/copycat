"""
Manual composition tests for Phase 2.

Usage:
  uv run python -m backend.scripts.test_composition "organize files then open folder"
  uv run python -m backend.scripts.test_composition --resolve-only "do A then B"

Requires accepted skills in Supabase and GEMINI_API_KEY(s) in .env.
"""

from __future__ import annotations

import argparse
import json
import sys

from backend.ai.skill_resolver import resolve_skills
from backend.storage.skills import get_accepted_skills
from backend.voice.command_bridge import run_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Test multi-skill composition")
    parser.add_argument("command", help="Natural-language command to test")
    parser.add_argument(
        "--resolve-only",
        action="store_true",
        help="Only run skill resolution, do not execute",
    )
    parser.add_argument(
        "--modality",
        choices=("text", "voice"),
        default="text",
        help="Request modality passed to execute pipeline",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print raw Gemini resolver output when resolution fails",
    )
    args = parser.parse_args()

    accepted = get_accepted_skills()
    if not accepted:
        print("No accepted skills found. Accept at least one skill first.")
        return 1

    print(f"Accepted skills: {len(accepted)}")
    for skill in accepted:
        print(f"  - {skill.get('name')} ({skill.get('id')})")

    resolution = resolve_skills(args.command, accepted)
    print("\n--- Resolution ---")
    if resolution is None:
        print("No matching skills.")
        if args.verbose:
            _print_raw_resolution(args.command, accepted)
        return 0

    print(json.dumps(resolution.model_dump(), indent=2))

    if args.resolve_only:
        return 0

    print("\n--- Execute ---")
    result = run_command(args.command, modality=args.modality)
    print(json.dumps(
        {
            "resolved_skills": [s.model_dump() for s in result.resolved_skills],
            "skill_runs": [r.model_dump() for r in result.skill_runs],
            "reply": result.reply.model_dump(),
            "stopped_at_order": result.stopped_at_order,
        },
        indent=2,
    ))
    return 0


def _print_raw_resolution(command: str, skills: list[dict]) -> None:
    import backend.ai.skill_resolver as skill_resolver
    from backend.ai.gemini_client import call_gemini
    from backend.env_config import get_gemini_text_model

    prompt_skills = skill_resolver._trim_skills_for_prompt(skills)
    prompt = f'Resolve skills for: "{command}" from {json.dumps(prompt_skills)}'
    print("\n--- Verbose (raw model output) ---")
    print(f"model: {get_gemini_text_model()}")

    try:
        response = call_gemini(
            model=get_gemini_text_model(),
            contents=prompt,
        )
        print(response.text)
    except Exception as error:
        print(f"Resolver call failed: {error}")


if __name__ == "__main__":
    sys.exit(main())
