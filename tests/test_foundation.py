"""Basic foundation tests for Agentic Career Lab models and settings."""

import pytest
from pydantic import ValidationError

from agentic_career_lab.config import Settings
from agentic_career_lab.models import (
    EvidenceStatus,
    LearningPlan,
    Opportunity,
    OpportunityRequirement,
    RequirementType,
    ResumeEvidence,
    SkillGap,
    StudentProfile,
)


def test_settings_defaults():
    """Verify default settings configuration."""
    settings = Settings(
        google_cloud_project="test-project",
        google_cloud_location="us-central1",
    )
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.gemma_model == "gemma4:12b"
    assert settings.gemini_model == "gemini-1.5-flash"
    assert settings.google_cloud_project == "test-project"


def test_student_profile_creation():
    """Verify StudentProfile initialization and validation."""
    profile = StudentProfile(
        name="Alex Chen",
        target_role="AI Engineering Intern",
        education_level="Junior",
        major="Computer Science",
        skills=["Python", "SQL", "Docker"],
        interests=["LLM Agents", "Cloud Infrastructure"],
    )
    assert profile.name == "Alex Chen"
    assert len(profile.skills) == 3
    assert profile.resume_text is None


def test_opportunity_model():
    """Verify Opportunity model and strict URL validation."""
    opp = Opportunity(
        opportunity_id="opp-101",
        role="Cloud Software Engineer Intern",
        company="Google",
        location="Sunnyvale, CA",
        source_url="https://careers.google.com/jobs/results/123",  # type: ignore[arg-type]
        description="Software engineering internship focused on cloud services.",
        requirements=[
            OpportunityRequirement(
                skill="Python",
                req_type=RequirementType.REQUIRED,
                context="3+ months hands-on Python experience",
            ),
            OpportunityRequirement(
                skill="Kubernetes",
                req_type=RequirementType.PREFERRED,
                context="Familiarity with container orchestration",
            ),
        ],
        why_relevant="Directly matches student coursework in distributed computing.",
    )
    assert opp.company == "Google"
    assert len(opp.requirements) == 2
    assert opp.requirements[0].req_type == RequirementType.REQUIRED
    assert opp.requirements[1].req_type == RequirementType.PREFERRED


def test_opportunity_invalid_url():
    """Verify that invalid URLs fail schema validation."""
    with pytest.raises(ValidationError):
        Opportunity(
            opportunity_id="opp-invalid",
            role="Intern",
            company="Acme Corp",
            location="Remote",
            source_url="not-a-valid-url",  # type: ignore[arg-type]
            description="Sample desc",
        )


def test_resume_evidence_and_skill_gap():
    """Verify ResumeEvidence and SkillGap models."""
    evidence = ResumeEvidence(
        skills=["Python", "Docker"],
        education=["B.S. in Computer Science, 2026"],
        unsupported_claims_detected=[],
    )
    gap = SkillGap(
        skill="Vertex AI",
        status=EvidenceStatus.MISSING,
        requirement_type=RequirementType.REQUIRED,
        explanation="No mention of Vertex AI or cloud ML APIs found in resume.",
    )
    assert "Python" in evidence.skills
    assert gap.status == EvidenceStatus.MISSING
    assert gap.resume_evidence is None


def test_learning_plan_creation():
    """Verify LearningPlan structure."""
    plan = LearningPlan(
        opportunity_id="opp-101",
        target_role="AI Engineering Intern",
        duration_weeks=4,
        weekly_milestones=[
            {"week": 1, "topic": "Vertex AI SDK & Gemini API", "status": "pending"},
            {"week": 2, "topic": "Google ADK Multi-Agent Coordinator", "status": "pending"},
        ],
        recommended_portfolio_project={
            "title": "Multi-Agent Research Assistant",
            "technologies": ["Python", "Vertex AI", "Google ADK"],
        },
    )
    assert plan.duration_weeks == 4
    assert len(plan.weekly_milestones) == 2
    assert "Vertex AI" in plan.recommended_portfolio_project["technologies"]


def test_app_imports_and_no_live_calls():
    """Verify that the app can be imported without executing live API calls."""
    try:
        import agentic_career_lab.app  # noqa: F401

        assert True
    except Exception as e:
        pytest.fail(f"App module failed to import: {e}")


def test_demo_profile_and_presets_exist():
    """Verify that the app contains the demo values requested."""
    with open("src/agentic_career_lab/app.py", encoding="utf-8") as f:
        content = f.read()

    assert "Computer Science" in content
    assert "2027" in content
    assert "AI Engineering Intern" in content
    assert "Python, SQL, Docker, Google Cloud, REST APIs" in content

    # Presets
    assert (
        "I'm a junior computer science student. I know Python, SQL, Docker, and basic Google Cloud."
    ) in content
    assert "Compare my resume against the selected AI Engineering Intern role." in content
    assert (
        "Based on the selected internship and my current evidence, identify my top three skill gaps"
    ) in content
    assert "Find an AI/cloud internship that fits my profile" in content
