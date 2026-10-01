from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.agents.skill_builder.planner import FakePlanningLLM
from agentic_career_lab.models import (
    EvidenceStatus,
    Opportunity,
    OpportunityRequirement,
    RequirementEvidenceMatch,
    RequirementType,
    ResumeAnalysis,
)


def test_skill_builder_deterministic_gaps():
    agent = SkillBuilderAgent(llm=FakePlanningLLM())

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
            OpportunityRequirement(skill="Google Cloud", req_type=RequirementType.PREFERRED),
        ],
    )

    resume_analysis = ResumeAnalysis(
        requirement_matches=[
            RequirementEvidenceMatch(requirement="Python", status=EvidenceStatus.DEMONSTRATED),
            RequirementEvidenceMatch(requirement="Google Cloud", status=EvidenceStatus.PARTIAL),
        ]
    )

    plan = agent.run(opp, resume_analysis, 2)

    assert "Python" in plan.strengths

    missing_gap = next(g for g in plan.priority_gaps if g.skill == "Kubernetes")
    assert missing_gap.status == EvidenceStatus.MISSING
    assert missing_gap.priority == "High"

    partial_gap = next(g for g in plan.priority_gaps if g.skill == "Google Cloud")
    assert partial_gap.status == EvidenceStatus.PARTIAL
    assert partial_gap.priority == "Low"  # Preferred + Partial = Low

    assert len(plan.learning_steps) == 2
    assert plan.portfolio_project is not None
    assert "Kubernetes" in plan.portfolio_project.skills_practiced

    assert any(res.skill == "Kubernetes" for res in plan.recommended_resources)
    assert (
        any(res.skill == "Vertex AI" for res in plan.recommended_resources)
        if "Vertex AI" in [req.skill for req in opp.requirements]
        else True
    )
