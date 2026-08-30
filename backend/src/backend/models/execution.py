from typing import Any

from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    command: str


class SkillParameter(BaseModel):
    name: str
    value: Any


class ResolvedSkill(BaseModel):
    skill_id: str
    skill_name: str
    environment: str
    parameters: list[SkillParameter]
    match_confidence: str
    reasoning: str


class ExecutionPlanStep(BaseModel):
    step_number: int

    # Windows steps are restricted to a fixed verb set, enforced at
    # execution time in executors/windows.py. Browser steps are free-form
    # descriptions of the demonstrated workflow - the browser executor's
    # agent reasons over live page state rather than following pre-scripted
    # action names, so there's no fixed enum for those.
    action: str

    description: str

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )


class ExecutionPlan(BaseModel):
    skill_id: str
    skill_name: str
    environment: str
    goal: str
    parameters: list[SkillParameter]
    steps: list[ExecutionPlanStep]


class StepExecutionResult(BaseModel):
    step_number: int
    action: str
    success: bool
    message: str
    details: dict[str, Any] = Field(
        default_factory=dict
    )


class ExecutionResult(BaseModel):
    success: bool
    message: str
    skill_id: str

    details: dict[str, Any] = Field(
        default_factory=dict
    )