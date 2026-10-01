import pytest
from pydantic import ValidationError

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.agents.job_scout.matcher import Matcher
from agentic_career_lab.agents.job_scout.requirement_extractor import RequirementExtractor
from agentic_career_lab.models import (
    Opportunity,
    OpportunityRequirement,
    OpportunitySearchQuery,
    RequirementType,
    StudentProfile,
)
from agentic_career_lab.providers.mock import MockOpportunityProvider
from agentic_career_lab.services.skill_normalizer import SkillNormalizer


def test_mock_provider_returns_deterministic_opportunities():
    provider = MockOpportunityProvider()
    query = OpportunitySearchQuery(
        role="Intern", location="Texas", internship_only=True, keywords=[]
    )
    results = provider.search(query)

    assert len(results) == 2
    assert results[0].role == "AI Engineering Intern"
    assert "demo" in results[0].why_relevant.lower()


def test_invalid_external_opportunity_without_source_url():
    with pytest.raises(ValidationError):
        Opportunity(
            opportunity_id="invalid",
            role="Intern",
            company="Test",
            location="Remote",
            source_url="not-a-url",  # type: ignore[arg-type]
            description="Test",
        )


def test_requirement_extraction():
    extractor = RequirementExtractor()
    desc = "Need Python, Docker, Google Cloud and Kubernetes."
    reqs = extractor.extract(desc)

    skills = [r.skill for r in reqs]
    assert "Python" in skills
    assert "Docker" in skills
    assert "Google Cloud" in skills
    assert "Kubernetes" in skills

    # Check types
    for r in reqs:
        if r.skill == "Kubernetes":
            assert r.req_type == RequirementType.PREFERRED
        elif r.skill in ("Python", "Docker", "Google Cloud"):
            assert r.req_type == RequirementType.REQUIRED


def test_skill_normalization():
    normalizer = SkillNormalizer()
    assert normalizer.normalize("GCP") == "Google Cloud"
    assert normalizer.normalize("k8s") == "Kubernetes"
    assert normalizer.normalize(" Python ") == "Python"


def test_matching_logic():
    normalizer = SkillNormalizer()
    matcher = Matcher(normalizer)

    profile = StudentProfile(
        name="Test",
        target_role="Intern",
        education_level="Junior",
        major="CS",
        skills=["Python", "SQL", "Docker", "GCP"],
        interests=[],
    )

    opp = Opportunity(
        opportunity_id="1",
        role="Test",
        company="Test",
        location="Test",
        source_url="https://example.com/job",  # type: ignore[arg-type]
        description="Test",
        requirements=[
            OpportunityRequirement(skill="Python", req_type=RequirementType.REQUIRED),
            OpportunityRequirement(skill="Docker", req_type=RequirementType.REQUIRED),
            OpportunityRequirement(skill="Vertex AI", req_type=RequirementType.REQUIRED),
            OpportunityRequirement(skill="Kubernetes", req_type=RequirementType.REQUIRED),
        ],
    )

    match = matcher.match(profile, opp)

    assert set(match.demonstrated_skills) == {"Python", "Docker"}
    # GCP does not match Vertex AI or Kubernetes directly, but maybe as partial if logic catches it.
    # Actually wait, Vertex AI and K8s are missing.
    assert "Vertex AI" in match.missing_skills
    assert "Kubernetes" in match.missing_skills

    # Does not invent student skills or job reqs
    assert len(match.demonstrated_skills) + len(match.partial_skills) + len(
        match.missing_skills
    ) == len(opp.requirements)


def test_job_scout_agent():
    agent = JobScoutAgent(provider=MockOpportunityProvider())
    profile = StudentProfile(
        name="Test",
        target_role="Intern",
        education_level="Junior",
        major="CS",
        skills=["Python"],
        interests=[],
    )
    query = OpportunitySearchQuery(
        role="Intern", location="Texas", internship_only=True, keywords=[]
    )

    matches = agent.run(profile, query)
    assert len(matches) == 2
    assert len(agent.events) > 0

    for event in agent.events:
        assert "task_type" in event
        assert "status" in event
