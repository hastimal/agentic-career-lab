import pytest
from agentic_career_lab.agents.resume_agent.agent import PrivateResumeAgent
from agentic_career_lab.llm.local import FakeGemmaClient
from agentic_career_lab.models import (
    Opportunity,
    OpportunityRequirement,
    RequirementType,
    ResumeSuggestion,
    ResumeEvidence,
)
from agentic_career_lab.services.skill_normalizer import SkillNormalizer
from agentic_career_lab.agents.resume_agent.validator import ClaimValidator


def test_resume_missing_ollama_fails_safely():
    client = FakeGemmaClient(is_online=False)
    agent = PrivateResumeAgent(llm=client)
    with pytest.raises(RuntimeError, match="Ollama is not reachable"):
        agent.run(resume_text="Some text", opportunity=None)


def test_privacy_no_cloud_fallback():
    # If Ollama is offline, it raises an error, not switching to Gemini
    client = FakeGemmaClient(is_online=False)
    agent = PrivateResumeAgent(llm=client)
    try:
        agent.run(resume_text="Resume", opportunity=None)
    except RuntimeError:
        pass

    # We can check there is no gemini logic invoked
    events = [e["step"] for e in agent.events]
    assert "check_ollama" in events
    assert "extract_resume_evidence" not in events


def test_claim_validator_flags_invented_claims():
    normalizer = SkillNormalizer()
    validator = ClaimValidator(normalizer)

    evidence = ResumeEvidence(skills=["Python"], technologies=["Python"])

    suggestion = ResumeSuggestion(
        original_text="Built APIs.",
        suggested_text="Built Kubernetes clusters for 10,000 users.",
        evidence_used=["Kubernetes"],
    )

    validated = validator.validate(suggestion, evidence)
    assert not validated.accepted
    assert any("Kubernetes" in flag for flag in validated.unsupported_claims_detected)
    assert any("10,000" in flag for flag in validated.unsupported_claims_detected)


def test_resume_analysis_works_with_fake_model():
    client = FakeGemmaClient(is_online=True)
    agent = PrivateResumeAgent(llm=client)

    opp = Opportunity(
        opportunity_id="1",
        role="Test",
        company="Test",
        location="Test",
        source_url="https://example.com",  # type: ignore[arg-type]
        description="Test",
        requirements=[
            OpportunityRequirement(skill="Python", req_type=RequirementType.REQUIRED),
            OpportunityRequirement(skill="Kubernetes", req_type=RequirementType.REQUIRED),
        ],
    )

    analysis = agent.run("Built Python REST API.", opp)

    # Extract evidence has Python, Docker, SQL, REST APIs, Google Cloud from the fake model
    skills = [
        req.requirement for req in analysis.requirement_matches if req.status == "Demonstrated"
    ]
    assert "Python" in skills
    missing = [req.requirement for req in analysis.requirement_matches if req.status == "Missing"]
    assert "Kubernetes" in missing

    assert len(analysis.suggestions) > 0
