from typing import Any, Optional

from pydantic import BaseModel


class ObservableFact(BaseModel):
    item: Optional[str] = None
    item_type: Optional[str] = None
    source_location: Optional[str] = None
    destination: Optional[str] = None


class Action(BaseModel):
    type: str


class InferredDecision(BaseModel):
    description: str
    confidence: str


class Observation(BaseModel):
    observable_fact: ObservableFact
    action: Action
    inferred_decision: InferredDecision


class CandidateSkillStep(BaseModel):
    step_number: int
    action: str
    description: str
    observed_data: dict[str, Any] | None = None


class CandidateSkill(BaseModel):
    id: Optional[str] = None

    name: str
    description: str

    environment: str

    steps: list[CandidateSkillStep]

    confidence: str

    requires_user_validation: bool = True

    status: str = "pending"


class LearningResult(BaseModel):
    goal: str

    observations: list[Observation]

    candidate_skills: list[CandidateSkill]