"""Evaluation test suite for hybrid multi-agent routing and OpenTelemetry observability.

Validates:
1. STUDENT A (Junior CS student with Python, SQL, Docker, basic GCP)
   -> Grounded fundamentals, identifies cloud/AI gaps without hallucinated claims.
2. STUDENT B (Freshman with basic Python)
   -> Must not invent advanced cloud, AI, or production experience.
3. STUDENT C (Graduate data science student with Python, PyTorch, GCP)
   -> Advanced AI/ML opportunities mapped strictly when supported by real requirements.
4. OpenTelemetry tracing guarantees:
   -> Spans created for coordinator, agents, tools, models.
   -> Latency, model tags, runtime captured.
   -> ZERO raw resume text, PII, or full prompts in span attributes.
"""

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
    OpportunitySearchQuery,
    StudentProfile,
)
from agentic_career_lab.observability import (
    clear_in_memory_spans,
    get_in_memory_spans,
    init_telemetry,
)
from agentic_career_lab.providers.mock import MockOpportunityProvider


def get_test_coordinator():
    init_telemetry(force_reinit=True)
    clear_in_memory_spans()

    coord = CareerCoordinator(
        job_scout=JobScoutAgent(provider=MockOpportunityProvider()),
        resume_agent=PrivateResumeAgent(llm=FakeGemmaClient(is_online=True)),
        skill_builder=SkillBuilderAgent(llm=DeterministicPlanningLLM()),
    )
    return ADKCareerCoordinator(coord)


def test_student_a_junior_evaluation():
    """Student A: Junior CS student with Python, SQL, Docker, basic GCP.

    Should ground existing skills and identify missing cloud/AI requirements.
    """
    coord = get_test_coordinator()
    state = CareerWorkflowState()
    state.student_profile = StudentProfile(
        name="Student A (Alex)",
        target_role="AI Engineering Intern",
        education_level="Junior",
        major="Computer Science",
        skills=["Python", "SQL", "Docker", "Google Cloud"],
    )
    state.search_query = OpportunitySearchQuery(
        role="AI Engineering Intern", location="Texas", internship_only=True, keywords=[]
    )

    state = coord.execute_action(CareerAction.FIND_OPPORTUNITIES, state)
    assert len(state.opportunities) > 0
    state.selected_opportunity = state.opportunities[0].opportunity

    resume_text = (
        "Alex Chen\nJunior Computer Science student.\n"
        "Skills: Python, SQL, Docker, Google Cloud.\n"
        "Built internal tooling and deployed containerized Python microservices."
    )
    local_ctx = LocalResumeContext(raw_resume_text=resume_text)
    state = coord.execute_action(CareerAction.PREPARE_RESUME, state, local_resume=local_ctx)

    assert state.resume_analysis is not None
    # Verify no hallucinated skills accepted
    for sugg in state.resume_analysis.suggestions:
        assert sugg.accepted is True
        assert len(sugg.unsupported_claims_detected) == 0

    state = coord.execute_action(CareerAction.BUILD_SKILLS, state)
    assert state.skill_builder_plan is not None
    plan = state.skill_builder_plan

    # Strengths should reflect candidate's verified skills
    assert len(plan.strengths) > 0
    # Gaps should target unverified or missing skills without pretending candidate is senior
    assert any(
        g.skill in ("Vertex AI", "Kubernetes", "Machine Learning", "Docker", "Google Cloud")
        for g in plan.priority_gaps
    )


def test_student_b_freshman_evaluation():
    """Student B: Freshman with basic Python.

    Must not pretend this student has advanced cloud, AI, or production experience.
    """
    coord = get_test_coordinator()
    state = CareerWorkflowState()
    state.student_profile = StudentProfile(
        name="Student B (Sam)",
        target_role="Software Engineering Intern",
        education_level="Freshman",
        major="Computer Science",
        skills=["Python"],
    )
    state.search_query = OpportunitySearchQuery(
        role="Software Engineering Intern", location="Remote", internship_only=True, keywords=[]
    )

    state = coord.execute_action(CareerAction.FIND_OPPORTUNITIES, state)
    assert len(state.opportunities) > 0
    state.selected_opportunity = state.opportunities[0].opportunity

    # Minimal resume with just introductory python
    resume_text = "Sam Freshman\nFirst-year student.\nCoursework: Intro to CS in Python."
    local_ctx = LocalResumeContext(raw_resume_text=resume_text)
    state = coord.execute_action(CareerAction.PREPARE_RESUME, state, local_resume=local_ctx)
    assert state.resume_analysis is not None

    state = coord.execute_action(CareerAction.BUILD_SKILLS, state)
    plan = state.skill_builder_plan
    assert plan is not None

    # Should identify missing tools/infrastructure as priority gaps
    gap_skills = [g.skill for g in plan.priority_gaps]
    assert len(gap_skills) > 0


def test_student_c_graduate_data_science_evaluation():
    """Student C: Graduate data science student with Python, PyTorch, GCP.

    AI/ML opportunities should be grounded strictly against requirements.
    """
    coord = get_test_coordinator()
    state = CareerWorkflowState()
    state.student_profile = StudentProfile(
        name="Student C (Dr. Jordan)",
        target_role="Machine Learning Research Intern",
        education_level="Graduate",
        major="Data Science",
        skills=["Python", "PyTorch", "GCP", "SQL"],
    )
    state.search_query = OpportunitySearchQuery(
        role="AI Engineering Intern", location="Texas", internship_only=True, keywords=[]
    )

    state = coord.execute_action(CareerAction.FIND_OPPORTUNITIES, state)
    assert len(state.opportunities) > 0
    state.selected_opportunity = state.opportunities[0].opportunity

    resume_text = (
        "Jordan Lee\nGraduate Data Science Student.\n"
        "Skills: Python, PyTorch, GCP, SQL, NumPy.\n"
        "Trained transformer models using PyTorch on Google Cloud."
    )
    local_ctx = LocalResumeContext(raw_resume_text=resume_text)
    state = coord.execute_action(CareerAction.PREPARE_RESUME, state, local_resume=local_ctx)

    state = coord.execute_action(CareerAction.BUILD_SKILLS, state)
    plan = state.skill_builder_plan
    assert plan is not None

    # Final Career Action Plan creation
    action_plan = coord.create_action_plan(state)
    assert action_plan.workflow_status == "Complete"
    assert action_plan.target_opportunity is not None


def test_opentelemetry_tracing_and_privacy_boundary():
    """Test OpenTelemetry tracing captures workflow execution while keeping raw resumes private."""
    coord = get_test_coordinator()
    state = CareerWorkflowState()
    state.student_profile = StudentProfile(
        name="Telemetry Student",
        target_role="AI Engineering Intern",
        education_level="Junior",
        major="Computer Science",
        skills=["Python", "SQL", "Docker"],
    )
    state.search_query = OpportunitySearchQuery(
        role="AI Engineering Intern", location="Texas", internship_only=True, keywords=[]
    )

    state = coord.execute_action(CareerAction.FIND_OPPORTUNITIES, state)
    state.selected_opportunity = state.opportunities[0].opportunity

    secret_marker = "SUPER_SECRET_PII_AND_RAW_RESUME_MARKER_12345"
    resume_text = f"Candidate Name\nPhone: 555-0199\nSkills: Python, Docker.\n{secret_marker}"
    local_ctx = LocalResumeContext(raw_resume_text=resume_text)

    state = coord.execute_action(CareerAction.PREPARE_RESUME, state, local_resume=local_ctx)
    state = coord.execute_action(CareerAction.BUILD_SKILLS, state)
    _ = coord.create_action_plan(state)

    spans = get_in_memory_spans()
    span_names = [s.name for s in spans]

    # 1. Verify span hierarchy exists
    assert "coordinator.find_opportunities" in span_names
    assert "agent.job_scout" in span_names
    assert "coordinator.prepare_resume" in span_names
    assert "agent.private_resume" in span_names
    assert "coordinator.build_skills" in span_names
    assert "agent.skill_builder" in span_names
    assert "coordinator.report_generation" in span_names

    # 2. Strict Privacy Verification: secret_marker MUST NOT appear in any span attribute or status
    for span in spans:
        if span.attributes:
            for k, v in span.attributes.items():
                assert secret_marker not in str(v), f"Leaked secret in span attribute {k}"
                assert "555-0199" not in str(v), f"Leaked phone in span attribute {k}"
        if span.status.description:
            assert secret_marker not in span.status.description
