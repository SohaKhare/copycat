from typing import Any

from pydantic import BaseModel


class Skill(BaseModel):
    name: str

    description: str

    steps: list[dict[str, Any]]

    environment: str

    confidence: str

    status: str = "pending"

    tested: bool = False


class EditSkillRequest(BaseModel):
    name: str | None = None

    description: str | None = None

    steps: list[dict[str, Any]] | None = None

    environment: str | None = None