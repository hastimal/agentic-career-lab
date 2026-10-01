from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from agentic_career_lab.coordinator.events import AgentExecutionEvent
from agentic_career_lab.models import OpportunitySearchQuery, StudentProfile


class CareerAction(StrEnum):
    FIND_OPPORTUNITIES = "find_opportunities"
    PREPARE_RESUME = "prepare_resume"
    BUILD_SKILLS = "build_skills"
    FULL_WORKFLOW = "full_workflow"


class LocalResumeContext(BaseModel):
    """Privacy boundary: Holds raw text only for local execution."""

    raw_resume_text: str


class CareerWorkflowState(BaseModel):
    student_profile: StudentProfile | None = None
    search_query: OpportunitySearchQuery | None = None
    opportunities: list[Any] = Field(default_factory=list)
    selected_opportunity: Any | None = None
    resume_source: str | None = None
    resume_analysis: Any | None = None
    skill_builder_plan: Any | None = None
    current_step: str | None = None
    completed_steps: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    activity_events: list[AgentExecutionEvent] = Field(default_factory=list)


class CareerActionPlan(BaseModel):
    target_opportunity: Any | None = None
    resume_evidence_summary: str | None = None
    priority_skill_gaps: list[Any] = Field(default_factory=list)
    recommended_resources: list[Any] = Field(default_factory=list)
    learning_plan: list[Any] = Field(default_factory=list)
    portfolio_project: Any | None = None
    workflow_status: str
