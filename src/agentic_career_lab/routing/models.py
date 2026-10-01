from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskType(StrEnum):
    OPPORTUNITY_SEARCH = "opportunity_search"
    REQUIREMENT_INTERPRETATION = "requirement_interpretation"
    RESUME_ANALYSIS = "resume_analysis"
    RESUME_REWRITE = "resume_rewrite"
    SKILL_MATCHING = "skill_matching"
    GAP_ANALYSIS = "gap_analysis"
    LEARNING_PLAN = "learning_plan"
    RESOURCE_LOOKUP = "resource_lookup"
    PORTFOLIO_PROJECT = "portfolio_project"
    CLAIM_VALIDATION = "claim_validation"


class RuntimeType(StrEnum):
    GEMINI_VERTEX = "gemini_vertex"
    GEMMA_OLLAMA = "gemma_ollama"
    PYTHON = "python"


class PrivacyLevel(StrEnum):
    PUBLIC = "public"
    STRUCTURED = "structured"
    PRIVATE = "private"


class RoutingDecision(BaseModel):
    task_type: TaskType
    runtime: RuntimeType
    reason: str
    privacy_level: PrivacyLevel
    cloud_allowed: bool
    fallback_allowed: bool
    model_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RoutingEvent(BaseModel):
    task_type: str
    runtime: str
    model_name: str | None = None
    reason: str
    privacy_level: str
    fallback_used: bool = False
    status: str = "success"
    duration_ms: float = 0.0


class CloudPlanningContext(BaseModel):
    target_role: str
    required_skills: list[str]
    demonstrated_skills: list[str]
    partial_skills: list[str]
    missing_skills: list[str]
    plan_duration_weeks: int
