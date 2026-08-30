from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ExecuteRequest(BaseModel):
    # Either a typed command or base64 audio (Gemini transcribes it). `modality`
    # decides whether the reply is spoken back - "speak only on voice turns".
    command: str | None = None
    audio_b64: str | None = None
    audio_format: str = "webm"
    modality: Literal["text", "voice"] = "text"

    @model_validator(mode="after")
    def _need_input(self) -> "ExecuteRequest":
        if not self.command and not self.audio_b64:
            raise ValueError(
                "Provide either 'command' or 'audio_b64'."
            )
        return self


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


class ResolvedSkillItem(BaseModel):
    skill_id: str
    skill_name: str
    environment: str
    parameters: list[SkillParameter]
    order: int
    match_confidence: str = "medium"

    def to_resolved_skill(self, reasoning: str = "") -> ResolvedSkill:
        return ResolvedSkill(
            skill_id=self.skill_id,
            skill_name=self.skill_name,
            environment=self.environment,
            parameters=self.parameters,
            match_confidence=self.match_confidence,
            reasoning=reasoning,
        )


class ResolveSkillsResult(BaseModel):
    skills: list[ResolvedSkillItem]
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


class SkillRunResult(BaseModel):
    order: int
    skill_id: str
    skill_name: str
    environment: str
    success: bool
    message: str
    execution_plan: ExecutionPlan
    execution_result: ExecutionResult
    execution_history: dict[str, Any] | None = None