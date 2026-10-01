import pytest

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.agents.resume_agent.agent import PrivateResumeAgent
from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.agents.skill_builder.planner import DeterministicPlanningLLM
from agentic_career_lab.coordinator.adk_coordinator import ADKCareerCoordinator
from agentic_career_lab.coordinator.career_coordinator import CareerCoordinator
from agentic_career_lab.coordinator.state import (
    CareerAction,
    CareerWorkflowState,
    LocalResumeContext,
)
from agentic_career_lab.llm.local import FakeGemmaClient
from agentic_career_lab.models import (
    Opportunity,
    OpportunityRequirement,
    OpportunitySearchQuery,
    StudentProfile,
)
from agentic_career_lab.providers.mock import MockOpportunityProvider


@pytest.fixture
def coordinator():
    domain = CareerCoordinator(
        job_scout=JobScoutAgent(provider=MockOpportunityProvider()),
        resume_agent=PrivateResumeAgent(llm=FakeGemmaClient(is_online=True)),
        skill_builder=SkillBuilderAgent(llm=DeterministicPlanningLLM()),
    )
    return ADKCareerCoordinator(domain)


def test_find_opportunities(coordinator):
    state = CareerWorkflowState(
        student_profile=StudentProfile(
            name="Alice", target_role="SWE", education_level="Senior", major="CS", skills=["Python"]
        ),
        search_query=OpportunitySearchQuery(
            role="SWE", location="Remote", internship_only=False, keywords=[]
        ),
    )
    result = coordinator.execute_action(CareerAction.FIND_OPPORTUNITIES, state)
    assert len(result.opportunities) > 0
    assert result.selected_opportunity is None
    assert "job_scout" in result.completed_steps


def test_prepare_resume_privacy(coordinator):
    state = CareerWorkflowState()
    # Mocking a previously selected opportunity
    state.selected_opportunity = Opportunity(
        opportunity_id="mock",
        role="SWE",
        company="Acme",
        location="Remote",
        source_url="https://example.com",
        description="Desc",
        requirements=[
            OpportunityRequirement(
                skill="Python", requirement="Python", category="Language", is_hard_requirement=True
            )
        ],
    )

    local_resume = LocalResumeContext(raw_resume_text="PRIVATE_RESUME_SECRET_12345")

    result = coordinator.execute_action(CareerAction.PREPARE_RESUME, state, local_resume)
    print("ERRORS:", result.errors)

    # Assert successful analysis
    assert result.resume_analysis is not None
    assert "private_resume" in result.completed_steps

    # Assert privacy boundary - raw resume text is NOT in generic state
    assert "PRIVATE_RESUME_SECRET_12345" not in str(result.model_dump())


def test_prepare_resume_failure_preserves_state():
    offline_resume_agent = PrivateResumeAgent(llm=FakeGemmaClient(is_online=False))
    coord = ADKCareerCoordinator(
        CareerCoordinator(
            job_scout=JobScoutAgent(provider=MockOpportunityProvider()),
            resume_agent=offline_resume_agent,
            skill_builder=SkillBuilderAgent(llm=DeterministicPlanningLLM()),
        )
    )
    state = CareerWorkflowState()
    state.selected_opportunity = Opportunity(
        opportunity_id="mock",
        role="SWE",
        company="Acme",
        location="Remote",
        source_url="https://example.com",
        description="Desc",
        requirements=[
            OpportunityRequirement(
                skill="Python", requirement="Python", category="Language", is_hard_requirement=True
            )
        ],
    )
    state.opportunities = ["Opp 1", "Opp 2"]

    local_resume = LocalResumeContext(raw_resume_text="Some text")

    result = coord.execute_action(CareerAction.PREPARE_RESUME, state, local_resume)

    # Assert failure cleanly captured
    assert result.resume_analysis is None
    assert len(result.errors) > 0
    assert "Failed" in [e.status for e in result.activity_events]

    # Assert previous state is preserved
    assert result.selected_opportunity == Opportunity(
        opportunity_id="mock",
        role="SWE",
        company="Acme",
        location="Remote",
        source_url="https://example.com",
        description="Desc",
        requirements=[
            OpportunityRequirement(
                skill="Python", requirement="Python", category="Language", is_hard_requirement=True
            )
        ],
    )
    assert result.opportunities == ["Opp 1", "Opp 2"]


def test_build_skills(coordinator):
    state = CareerWorkflowState()
    state.selected_opportunity = Opportunity(
        opportunity_id="mock",
        role="SWE",
        company="Acme",
        location="Remote",
        source_url="https://example.com",
        description="Desc",
        requirements=[
            OpportunityRequirement(
                skill="Python", requirement="Python", category="Language", is_hard_requirement=True
            )
        ],
    )
    # Mock resume analysis object that Skill Builder can parse
    from agentic_career_lab.models import ResumeAnalysis

    state.resume_analysis = ResumeAnalysis(
        demonstrated_evidence={"Python": ["Built app"]}, missing_evidence=["SQL"], suggestions=[]
    )

    result = coordinator.execute_action(CareerAction.BUILD_SKILLS, state)
    print("ERRORS:", result.errors)

    assert result.skill_builder_plan is not None
    assert len(result.skill_builder_plan.priority_gaps) > 0
    assert "skill_builder" in result.completed_steps


def test_full_offline_demo_test(coordinator):
    state = CareerWorkflowState(
        student_profile=StudentProfile(
            name="Alice",
            target_role="AI Engineer",
            education_level="Senior",
            major="CS",
            skills=["Python"],
        ),
        search_query=OpportunitySearchQuery(
            role="AI Engineer", location="Remote", internship_only=False, keywords=[]
        ),
    )
    local_resume = LocalResumeContext(
        raw_resume_text="Alice Student\nSkills: Python\nExperience: Built AI."
    )

    result = coordinator.execute_action(CareerAction.FULL_WORKFLOW, state, local_resume)
    print("ERRORS:", result.errors)

    assert result.selected_opportunity is not None
    assert result.resume_analysis is not None
    assert result.skill_builder_plan is not None
    assert "job_scout" in result.completed_steps
    assert "private_resume" in result.completed_steps
    assert "skill_builder" in result.completed_steps

    # Verify action plan
    plan = coordinator.create_action_plan(result)
    assert plan.target_opportunity is not None
    assert plan.portfolio_project is not None
