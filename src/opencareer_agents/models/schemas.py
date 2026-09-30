"""Core typed domain models for OpenCareer Agents."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class RequirementType(StrEnum):
    """Classification of job requirement."""

    REQUIRED = "required"
    PREFERRED = "preferred"


class EvidenceStatus(StrEnum):
    """Status of evidence match against requirements."""

    DEMONSTRATED = "Demonstrated"
    PARTIAL = "Partial"
    MISSING = "Missing"
    NOT_REQUIRED = "Not Required"


class StudentProfile(BaseModel):
    """Profile of a student seeking career opportunities."""

    student_id: str = Field(default="student-demo", description="Unique student identifier")
    name: str = Field(..., description="Student full name")
    target_role: str = Field(..., description="Desired role or career track")
    skills: list[str] = Field(default_factory=list, description="Verified self-reported skills")
    education_level: str = Field(..., description="E.g., Freshman, Junior, Graduate")
    major: str = Field(..., description="Field of study")
    interests: list[str] = Field(default_factory=list, description="Areas of technical interest")
    resume_text: str | None = Field(
        default=None,
        description="Local-only resume text (never transmitted to external cloud APIs)",
    )


class OpportunityRequirement(BaseModel):
    """Specific skill or experience requirement for an opportunity."""

    skill: str = Field(..., description="Canonical name of required skill or concept")
    req_type: RequirementType = Field(
        default=RequirementType.REQUIRED,
        description="Whether requirement is required or preferred",
    )
    context: str = Field(
        default="",
        description="Contextual snippet from job description explaining requirement",
    )


class Opportunity(BaseModel):
    """An opportunity/internship listing backed by verifiable evidence."""

    opportunity_id: str = Field(..., description="Unique ID for the opportunity")
    role: str = Field(..., description="Role title")
    company: str = Field(..., description="Hiring organization")
    location: str = Field(..., description="Job location or Remote status")
    source_url: HttpUrl = Field(..., description="Verifiable external source link")
    requirements: list[OpportunityRequirement] = Field(
        default_factory=list,
        description="Parsed requirements",
    )
    description: str = Field(..., description="Full or excerpted job description")
    why_relevant: str = Field(
        default="",
        description="Explanation of why this matches the student profile",
    )


class ResumeEvidence(BaseModel):
    """Evidence parsed locally from student's resume by Gemma."""

    skills: list[str] = Field(default_factory=list, description="Explicit skills found in resume")
    projects: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted project descriptions with technologies used",
    )
    experience: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Work, lab, or internship experiences",
    )
    education: list[str] = Field(
        default_factory=list,
        description="Verified degrees, courses, institutions",
    )
    unsupported_claims_detected: list[str] = Field(
        default_factory=list,
        description="Any fabricated or unverified claims flagged during validation",
    )


class SkillGap(BaseModel):
    """Comparison result between an opportunity requirement and resume evidence."""

    skill: str = Field(..., description="Skill being evaluated")
    status: EvidenceStatus = Field(..., description="Demonstrated, Partial, or Missing")
    requirement_type: RequirementType = Field(
        default=RequirementType.REQUIRED,
        description="Required or Preferred",
    )
    resume_evidence: str | None = Field(
        default=None,
        description="Direct resume snippet proving skill if present",
    )
    explanation: str = Field(
        default="",
        description="Explainable reasoning for this gap status",
    )


class LearningPlan(BaseModel):
    """Actionable, evidence-grounded skill acquisition plan."""

    opportunity_id: str = Field(..., description="Target opportunity ID")
    target_role: str = Field(..., description="Target role name")
    duration_weeks: int = Field(default=4, description="Roadmap timeline (e.g. 2 or 4 weeks)")
    weekly_milestones: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Prioritized milestones for addressing critical gaps",
    )
    recommended_portfolio_project: dict[str, Any] = Field(
        default_factory=dict,
        description="Practical portfolio project directly demonstrating missing skills",
    )
