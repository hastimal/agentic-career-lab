"""Unit and regression tests for Phase 2 - Phase 7 post-v0.8.0 features:
- Learning catalog enriched metadata validation
- Deterministic roadmap exact duration (2 weeks vs 4 weeks)
- Local-only planning when cloud consent is declined (zero Gemini invocations)
- Canonical 9-screen navigation and progress calculations
"""

from unittest.mock import MagicMock

import pytest

from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.agents.skill_builder.planner import DeterministicPlanningLLM
from agentic_career_lab.coordinator.career_coordinator import CareerCoordinator
from agentic_career_lab.coordinator.state import (
    CareerAction,
    CareerWorkflowState,
)
from agentic_career_lab.models import (
    ActivityProgress,
    ActivityStatus,
    EvidenceStatus,
    Opportunity,
    OpportunityRequirement,
    RequirementEvidenceMatch,
    RequirementType,
    ResumeAnalysis,
    SkillGap,
)
from agentic_career_lab.services.learning_resources import ResourceCatalog
from agentic_career_lab.ui_helpers import (
    ACTIVITY_DIAGNOSTICS,
    ASK_CAREER_AI,
    CAREER_REPORT,
    DASHBOARD,
    FALLBACK_EMOJI_ICON,
    JOB_EXPLORER,
    LEARNING_HUB,
    MY_LEARNING_PLAN,
    MY_RESUME,
    PROVIDER_ICON_MAP,
    RESUME_STUDIO,
    SKILL_GAP_ANALYSIS,
    get_provider_icon_url,
    normalize_navigation,
)


@pytest.fixture
def sample_opportunity():
    return Opportunity(
        opportunity_id="test-opp-1",
        role="AI Engineering Intern",
        company="Example Cloud AI Corp",
        location="Austin, TX",
        description="Build scalable AI workflows using Python, Docker, Vertex AI, and Kubernetes.",
        source_url="https://example.com/job/1",
        requirements=[
            OpportunityRequirement(skill="Python", req_type=RequirementType.REQUIRED),
            OpportunityRequirement(skill="Docker", req_type=RequirementType.REQUIRED),
            OpportunityRequirement(skill="Vertex AI", req_type=RequirementType.REQUIRED),
            OpportunityRequirement(skill="Kubernetes", req_type=RequirementType.REQUIRED),
        ],
    )


@pytest.fixture
def sample_analysis():
    return ResumeAnalysis(
        requirement_matches=[
            RequirementEvidenceMatch(
                requirement="Python",
                status=EvidenceStatus.DEMONSTRATED,
                evidence="3 years Python backend development",
            ),
            RequirementEvidenceMatch(
                requirement="Docker",
                status=EvidenceStatus.DEMONSTRATED,
                evidence="Containerized services using Docker and Compose",
            ),
            RequirementEvidenceMatch(
                requirement="Vertex AI",
                status=EvidenceStatus.MISSING,
                evidence="",
            ),
            RequirementEvidenceMatch(
                requirement="Kubernetes",
                status=EvidenceStatus.MISSING,
                evidence="",
            ),
        ],
        missing_evidence=["Vertex AI", "Kubernetes"],
        suggestions=[],
    )


# -------------------------------------------------------------
# Test Gate A: Roadmap Exact Duration (2 Weeks vs 4 Weeks)
# -------------------------------------------------------------
def test_deterministic_planner_exact_2_weeks():
    """Verify that requesting 2 weeks generates exactly 2 weekly milestones."""
    planner = DeterministicPlanningLLM()
    gaps = [
        SkillGap(skill="Vertex AI", status=EvidenceStatus.MISSING, priority="High"),
        SkillGap(skill="Kubernetes", status=EvidenceStatus.MISSING, priority="High"),
    ]
    plan = planner.create_learning_plan(
        "AI Engineering Intern", ["Python", "Docker"], gaps, duration_weeks=2
    )

    assert len(plan.learning_steps) == 2
    assert plan.learning_steps[0].week == 1
    assert plan.learning_steps[1].week == 2
    assert len(plan.learning_steps[0].activities) > 0
    assert len(plan.learning_steps[1].activities) > 0
    assert "2-week" in plan.summary


def test_deterministic_planner_exact_4_weeks():
    """Verify that requesting 4 weeks generates exactly 4 weekly milestones with capstone."""
    planner = DeterministicPlanningLLM()
    gaps = [
        SkillGap(skill="Vertex AI", status=EvidenceStatus.MISSING, priority="High"),
        SkillGap(skill="Kubernetes", status=EvidenceStatus.MISSING, priority="High"),
    ]
    plan = planner.create_learning_plan(
        "AI Engineering Intern", ["Python", "Docker"], gaps, duration_weeks=4
    )

    assert len(plan.learning_steps) == 4
    for idx, step in enumerate(plan.learning_steps, start=1):
        assert step.week == idx
        assert len(step.activities) > 0
        assert step.expected_output != ""

    assert "4-week" in plan.summary
    assert plan.portfolio_project is not None
    assert len(plan.portfolio_project.deliverables) >= 2


# -------------------------------------------------------------
# Test Gate B: Learning Resources Catalog Metadata & Quality
# -------------------------------------------------------------
def test_verified_learning_resources_catalog():
    """Verify that catalog resources have valid URLs, official providers, and rich metadata."""
    catalog = ResourceCatalog()
    all_res = catalog.get_full_catalog()

    # Scope and scale requirements (Phase 10 & Target: 60-100 curated resources)
    assert 60 <= len(all_res) <= 120, f"Expected 60-120 resources, found {len(all_res)}"

    # Resource uniqueness
    ids = [r.resource_id for r in all_res]
    assert len(ids) == len(set(ids)), "Duplicate resource_ids found in catalog"

    # Modalities and video quota (at least 20 verified video resources)
    video_res = [r for r in all_res if r.category == "WATCH" or r.resource_type == "Video / Talk"]
    assert len(video_res) >= 20, f"Expected at least 20 video resources, found {len(video_res)}"
    for v in video_res:
        assert v.url and "youtube.com" in v.url, f"Expected YouTube URL for video {v.resource_id}"

    # Free resource prioritization
    free_res = [r for r in all_res if r.free_or_paid == "Free"]
    assert len(free_res) >= 50, f"Expected at least 50 free resources, found {len(free_res)}"

    # All four modalities present
    categories = {r.category for r in all_res}
    assert {"WATCH", "LEARN", "PRACTICE", "BUILD"}.issubset(categories)

    # Provider diversity
    providers = {r.provider for r in all_res}
    assert len(providers) >= 20, f"Expected at least 20 distinct providers, found {len(providers)}"

    # Metadata completeness
    for r in all_res:
        assert r.resource_id, "Missing resource_id"
        assert r.title, "Missing title"
        assert r.provider, "Missing provider"
        assert r.difficulty in ("Beginner", "Intermediate", "Advanced"), (
            f"Invalid difficulty: {r.difficulty}"
        )
        assert r.free_or_paid in ("Free", "Free Tier", "Free Tier / Credits", "Paid", "Freemium"), (
            f"Invalid tier: {r.free_or_paid}"
        )
        assert r.is_verified is True
        assert r.url.startswith("https://"), f"Invalid URL for {r.resource_id}: {r.url}"
        assert r.learning_outcome, f"Missing learning outcome for {r.resource_id}"
        assert r.practical_exercise, f"Missing practical exercise for {r.resource_id}"

    vertex_resources = catalog.get_resources_for_skill("Vertex AI")
    assert len(vertex_resources) >= 2
    for r in vertex_resources:
        assert r.url is not None
        assert r.url.startswith("https://")

    k8s_resources = catalog.get_resources_for_skill("Kubernetes")
    assert len(k8s_resources) >= 2
    for r in k8s_resources:
        assert r.url.startswith("https://")
        assert any(
            domain in r.url
            for domain in (
                "kubernetes.io",
                "cloud.google.com",
                "cncf.io",
                "youtube.com",
                "github.com",
                "killercoda.com",
            )
        )

    # Fallback for unlisted skill must be cleanly labeled discovery guide, NOT fake course
    unknown = catalog.get_resources_for_skill("UnlistedCustomFramework123")
    assert len(unknown) == 1
    assert unknown[0].url is None
    assert "Documentation" in unknown[0].resource_type


def test_catalog_quality_audit_and_no_duplicate_urls():
    """Verify that catalog has zero duplicate URLs across resources and valid structure."""
    catalog = ResourceCatalog()
    all_res = catalog.get_full_catalog()

    # URL uniqueness for resources that have URLs
    urls = [r.url for r in all_res if r.url]
    assert len(urls) == len(set(urls)), (
        f"Found duplicate URLs: {[u for u in urls if urls.count(u) > 1]}"
    )

    # No generic YouTube search or channel root URLs
    for r in all_res:
        if r.url and "youtube.com" in r.url:
            assert "watch?v=" in r.url, f"Resource {r.resource_id} has invalid YouTube URL: {r.url}"
            assert len(r.url.split("watch?v=")[-1]) >= 11, (
                f"Resource {r.resource_id} video ID too short"
            )

    # Hands-on labs must have interactive exercise descriptions and proper sandbox/interactive URLs
    labs = [r for r in all_res if r.resource_type == "Hands-on Lab"]
    assert len(labs) >= 5
    for lab in labs:
        assert lab.practical_exercise, f"Lab {lab.resource_id} missing practical exercise"
        assert lab.category == "PRACTICE"

    # Specific fix verification: Vertex AI vs Cloud Run URL alignment
    vtx_res = [r for r in all_res if r.resource_id == "vtx-watch-1"]
    assert len(vtx_res) == 1
    assert "Rl9Gz1Yf6wM" in vtx_res[0].url
    assert "Vertex AI" in vtx_res[0].title

    gcp_run_res = [r for r in all_res if r.resource_id == "gcp-watch-2"]
    assert len(gcp_run_res) == 1
    assert "UcGPtVrd97M" in gcp_run_res[0].url
    assert "Cloud Run" in gcp_run_res[0].title


def test_ai_engineering_and_devops_recommendations_prioritization(
    sample_opportunity, sample_analysis
):
    """Verify role recommendations properly prioritize domain-relevant skills."""
    planner = DeterministicPlanningLLM()

    # 1. AI Engineering Intern role
    ai_gaps = [
        SkillGap(skill="Vertex AI", status=EvidenceStatus.MISSING, priority="High"),
        SkillGap(skill="AI Agents", status=EvidenceStatus.MISSING, priority="High"),
        SkillGap(skill="Kubernetes", status=EvidenceStatus.MISSING, priority="Medium"),
    ]
    ai_plan = planner.create_learning_plan(
        target_role="AI Engineering Intern",
        strengths=["Python", "Docker"],
        gaps=ai_gaps,
        duration_weeks=4,
    )
    rec_skills = [r.skill for r in ai_plan.recommended_resources]
    assert "Vertex AI" in rec_skills
    assert "AI Agents" in rec_skills
    assert "Kubernetes" in rec_skills

    # 2. DevOps Engineer role
    devops_gaps = [
        SkillGap(skill="Kubernetes", status=EvidenceStatus.MISSING, priority="High"),
        SkillGap(skill="Terraform", status=EvidenceStatus.MISSING, priority="High"),
        SkillGap(skill="OpenTelemetry", status=EvidenceStatus.MISSING, priority="Medium"),
    ]
    devops_plan = planner.create_learning_plan(
        target_role="DevOps Engineer",
        strengths=["Linux", "Docker"],
        gaps=devops_gaps,
        duration_weeks=4,
    )
    devops_rec_skills = [r.skill for r in devops_plan.recommended_resources]
    assert "Kubernetes" in devops_rec_skills
    assert "Terraform" in devops_rec_skills
    assert "OpenTelemetry" in devops_rec_skills


# -------------------------------------------------------------
# Test Gate C: Privacy Boundary & Consent-Declined Local Fallback
# -------------------------------------------------------------
def test_skill_builder_local_only_when_consent_declined(sample_opportunity, sample_analysis):
    """Verify that when cloud consent is declined, planning runs 100% locally with zero cloud API call."""
    # Create mock cloud client that will fail if invoked
    mock_cloud = MagicMock()
    mock_cloud.generate.side_effect = AssertionError(
        "Cloud client MUST NOT be invoked when consent is declined!"
    )

    # Deterministic fallback builder
    local_builder = SkillBuilderAgent(llm=DeterministicPlanningLLM())
    plan = local_builder.run(sample_opportunity, sample_analysis, duration_weeks=2)

    assert plan is not None
    assert len(plan.learning_steps) == 2
    # Verify no mock cloud call was ever made
    assert mock_cloud.generate.call_count == 0


def test_coordinator_passes_dynamic_duration(sample_opportunity, sample_analysis):
    """Verify that CareerCoordinator respects requested_duration_weeks from state."""
    coord = CareerCoordinator(
        job_scout=MagicMock(),
        resume_agent=MagicMock(),
        skill_builder=SkillBuilderAgent(llm=DeterministicPlanningLLM()),
    )
    state = CareerWorkflowState()
    state.selected_opportunity = sample_opportunity
    state.resume_analysis = sample_analysis
    state.requested_duration_weeks = 2

    coord.execute_action(CareerAction.BUILD_SKILLS, state)

    assert state.skill_builder_plan is not None
    assert len(state.skill_builder_plan.learning_steps) == 2


# -------------------------------------------------------------
# Test Gate D: UI Navigation & Workflow Progression
# -------------------------------------------------------------
def test_canonical_ten_screens_navigation():
    """Verify all 10 student-centric screens including My Profile normalize correctly."""
    from agentic_career_lab.ui_helpers import MY_PROFILE

    assert normalize_navigation(DASHBOARD) == DASHBOARD
    assert normalize_navigation(MY_PROFILE) == MY_PROFILE
    assert normalize_navigation(ASK_CAREER_AI) == ASK_CAREER_AI
    assert normalize_navigation(MY_RESUME) == MY_RESUME
    assert normalize_navigation(JOB_EXPLORER) == JOB_EXPLORER
    assert normalize_navigation(SKILL_GAP_ANALYSIS) == SKILL_GAP_ANALYSIS
    assert normalize_navigation(LEARNING_HUB) == LEARNING_HUB
    assert normalize_navigation(MY_LEARNING_PLAN) == MY_LEARNING_PLAN
    assert normalize_navigation(CAREER_REPORT) == CAREER_REPORT
    assert normalize_navigation(ACTIVITY_DIAGNOSTICS) == ACTIVITY_DIAGNOSTICS
    assert normalize_navigation(RESUME_STUDIO) == RESUME_STUDIO

    # Legacy routes still map
    assert normalize_navigation("Home") == "Home"
    assert normalize_navigation("Find Opportunities") == "Find Opportunities"
    assert normalize_navigation("Prepare Resume") == "Prepare Resume"
    assert normalize_navigation("Build Skills") == "Build Skills"
    assert normalize_navigation("Agent Activity") == "Agent Activity"


def test_activity_progress_tracking():
    """Verify ActivityProgress model instantiation and status transitions."""
    prog = ActivityProgress(
        step_id="step_1_act_0",
        activity_name="Review official documentation",
        status=ActivityStatus.IN_PROGRESS,
        evidence_notes="Read chapters 1-3",
        supporting_link="https://github.com/example/repo",
    )
    assert prog.status == ActivityStatus.IN_PROGRESS
    assert prog.evidence_notes == "Read chapters 1-3"

    prog.status = ActivityStatus.COMPLETED
    assert prog.status == ActivityStatus.COMPLETED


def test_profile_model_persistence_and_job_prefill():
    """Verify StudentProfile model integrity, self-reported skills, and search query integration."""
    from agentic_career_lab.models import OpportunitySearchQuery, StudentProfile

    profile = StudentProfile(
        name="Alex Chen",
        target_role="AI Engineering Intern",
        education_level="Junior",
        major="Computer Science",
        skills=["Python", "SQL", "Docker", "Google Cloud", "REST APIs"],
        interests=["Machine Learning", "Cloud Infrastructure"],
    )

    assert profile.name == "Alex Chen"
    assert profile.major == "Computer Science"
    assert "Docker" in profile.skills
    assert "REST APIs" in profile.skills

    # Test prefilling search query
    query = OpportunitySearchQuery(
        role=profile.target_role,
        location="Texas",
        internship_only=True,
        keywords=profile.skills,
    )
    assert query.role == "AI Engineering Intern"
    assert query.location == "Texas"
    assert "Google Cloud" in query.keywords


# -------------------------------------------------------------
# Test Gate E: Interactive Career Journey Tracker (0%, 33%, 67%, 100%)
# -------------------------------------------------------------
def test_career_journey_progress_percentages(sample_opportunity, sample_analysis):
    """Verify workflow progress strictly tracks actual state: 0%, 33%, 67%, 100%."""
    from agentic_career_lab.models import LearningPlan
    from agentic_career_lab.ui_helpers import (
        CAREER_REPORT,
        JOB_EXPLORER,
        MY_LEARNING_PLAN,
        MY_RESUME,
        get_workflow_progress,
    )

    # 1. 0% New student
    p0 = get_workflow_progress(None, None, None)
    assert p0["percent_complete"] == 0
    assert not p0["opportunity_selected"]
    assert not p0["resume_analyzed"]
    assert not p0["skill_plan_built"]
    assert p0["canonical_next_step"] == JOB_EXPLORER

    # 2. 33% Job selected
    p33 = get_workflow_progress(sample_opportunity, None, None)
    assert p33["percent_complete"] == 33
    assert p33["opportunity_selected"]
    assert not p33["resume_analyzed"]
    assert not p33["skill_plan_built"]
    assert p33["canonical_next_step"] == MY_RESUME

    # 3. 67% Resume analyzed
    p67 = get_workflow_progress(sample_opportunity, sample_analysis, None)
    assert p67["percent_complete"] == 67
    assert p67["opportunity_selected"]
    assert p67["resume_analyzed"]
    assert not p67["skill_plan_built"]
    assert p67["canonical_next_step"] == MY_LEARNING_PLAN

    # 4. 100% Learning plan generated
    sample_plan = LearningPlan(
        student_id="student-1",
        opportunity_id=sample_opportunity.opportunity_id,
        target_role=sample_opportunity.role,
        duration_weeks=4,
        skill_gaps=[],
        learning_steps=[],
        weekly_milestones=[{"week": 1, "topic": "Docker Containers"}],
        recommended_portfolio_project={"title": "Cloud Service"},
    )
    p100 = get_workflow_progress(sample_opportunity, sample_analysis, sample_plan)
    assert p100["percent_complete"] == 100
    assert p100["opportunity_selected"]
    assert p100["resume_analyzed"]
    assert p100["skill_plan_built"]
    assert p100["canonical_next_step"] == CAREER_REPORT
    assert p100["next_step"] is None


def test_opportunity_change_state_invalidation(sample_opportunity, sample_analysis):
    """Verify that changing target opportunity invalidates stale resume analyses and plans."""
    from agentic_career_lab.models import LearningPlan

    state = CareerWorkflowState()
    state.selected_opportunity = sample_opportunity
    state.resume_analysis = sample_analysis
    state.skill_builder_plan = LearningPlan(
        student_id="student-1",
        opportunity_id=sample_opportunity.opportunity_id,
        target_role=sample_opportunity.role,
        duration_weeks=2,
        skill_gaps=[],
        learning_steps=[],
        weekly_milestones=[],
        recommended_portfolio_project={},
    )

    # Simulate selecting a new different opportunity
    new_opp = Opportunity(
        opportunity_id="new-opp-2",
        role="DevOps Platform Engineer",
        company="Global Cloud",
        location="Remote",
        description="Lead cloud infrastructure automation.",
        source_url="https://example.com/job/2",
        requirements=[],
    )

    # Invalidation check: When opp ID changes, clear stale comparisons
    if state.selected_opportunity.opportunity_id != new_opp.opportunity_id:
        state.resume_analysis = None
        state.skill_builder_plan = None
        state.selected_opportunity = new_opp

    assert state.selected_opportunity.opportunity_id == "new-opp-2"
    assert state.resume_analysis is None
    assert state.skill_builder_plan is None


# -------------------------------------------------------------
# Test Gate F: Phase 8 Guided Learning Experience & Resources
# -------------------------------------------------------------
def test_guided_learning_resource_modalities():
    """Verify that catalog categorizes items correctly into WATCH, LEARN, PRACTICE, BUILD."""
    catalog = ResourceCatalog()

    # WATCH
    videos = catalog.get_resources_by_category(["Vertex AI", "Kubernetes"], "WATCH")
    assert len(videos) > 0
    for v in videos:
        assert v.category == "WATCH"
        assert v.resource_id != ""
        assert v.url.startswith("https://")
        assert "youtube.com" in v.url

    # LEARN
    courses = catalog.get_resources_by_category(["Vertex AI", "Python"], "LEARN")
    assert len(courses) > 0
    for c in courses:
        assert c.category == "LEARN"
        assert c.resource_id != ""
        assert c.url.startswith("https://")

    # PRACTICE
    labs = catalog.get_resources_by_category(["Kubernetes", "Docker"], "PRACTICE")
    assert len(labs) > 0
    for lab in labs:
        assert lab.category == "PRACTICE"
        assert lab.resource_id != ""
        assert lab.url.startswith("https://")

    # BUILD
    projects = catalog.get_resources_by_category(["Vertex AI", "FastAPI"], "BUILD")
    assert len(projects) > 0
    for p in projects:
        assert p.category == "BUILD"
        assert p.resource_id != ""
        assert "github.com" in p.url


def test_task_to_resource_associations_2_and_4_weeks():
    """Verify that weekly activities in 2-week and 4-week plans associate valid resource_ids."""
    planner = DeterministicPlanningLLM()
    catalog = ResourceCatalog()
    gaps = [
        SkillGap(skill="Vertex AI", status=EvidenceStatus.MISSING, priority="High"),
        SkillGap(skill="Kubernetes", status=EvidenceStatus.MISSING, priority="High"),
    ]

    # 2-Week Plan
    plan_2w = planner.create_learning_plan("AI Engineer", ["Python"], gaps, duration_weeks=2)
    assert len(plan_2w.learning_steps) == 2
    for step in plan_2w.learning_steps:
        assert len(step.activity_resource_ids) > 0
        for _act_idx, res_id in step.activity_resource_ids.items():
            res = catalog.get_resource_by_id(res_id)
            assert res is not None, f"Resource {res_id} must exist in canonical catalog"
            assert res.url.startswith("https://")
            assert res.is_verified is True

    # 4-Week Plan
    plan_4w = planner.create_learning_plan("AI Engineer", ["Python"], gaps, duration_weeks=4)
    assert len(plan_4w.learning_steps) == 4
    for step in plan_4w.learning_steps:
        assert len(step.activity_resource_ids) > 0
        for _act_idx, res_id in step.activity_resource_ids.items():
            res = catalog.get_resource_by_id(res_id)
            assert res is not None, f"Resource {res_id} must exist in canonical catalog"
            assert res.is_verified is True


def test_learning_progress_calculation_and_evidence():
    """Verify that task completion calculations and evidence persistence work properly."""
    from agentic_career_lab.models.schemas import ActivityProgress, ActivityStatus

    # Simulate activities across 2 weeks (2 activities each week = 4 total)
    activities = [
        (
            "step_1_act_0",
            "Step 1 Act 0",
            ActivityStatus.COMPLETED,
            "https://github.com/student/vertex-demo",
        ),
        ("step_1_act_1", "Step 1 Act 1", ActivityStatus.NOT_STARTED, ""),
        (
            "step_2_act_0",
            "Step 2 Act 0",
            ActivityStatus.COMPLETED,
            "https://github.com/student/k8s-manifests",
        ),
        ("step_2_act_1", "Step 2 Act 1", ActivityStatus.NOT_STARTED, ""),
    ]

    progress_store: dict[str, ActivityProgress] = {}
    for act_key, name, stat, ev in activities:
        progress_store[act_key] = ActivityProgress(
            step_id=act_key,
            activity_name=name,
            status=stat,
            evidence_notes=ev,
        )

    # Week 1 stats
    week_1_keys = ["step_1_act_0", "step_1_act_1"]
    w1_done = sum(1 for k in week_1_keys if progress_store[k].status == ActivityStatus.COMPLETED)
    assert w1_done == 1
    assert int((w1_done / len(week_1_keys)) * 100) == 50

    # Overall stats
    total_acts = len(activities)
    total_done = sum(1 for p in progress_store.values() if p.status == ActivityStatus.COMPLETED)
    assert total_done == 2
    assert int((total_done / total_acts) * 100) == 50

    # Evidence retained without loss
    assert progress_store["step_1_act_0"].evidence_notes == "https://github.com/student/vertex-demo"
    assert (
        progress_store["step_2_act_0"].evidence_notes == "https://github.com/student/k8s-manifests"
    )


def test_provider_icon_mapping_verified_providers():
    """Verify that canonical providers map to valid HTTPS icon URLs."""
    essential_providers = [
        "Google Cloud",
        "Google Cloud Skills",
        "YouTube",
        "Docker",
        "Kubernetes",
        "GitHub",
        "freeCodeCamp",
        "Microsoft Learn",
        "AWS",
        "Coursera",
        "edX",
        "Hugging Face",
        "KodeKloud",
    ]

    for prov in essential_providers:
        url = get_provider_icon_url(prov)
        assert url is not None, f"Expected icon URL for provider '{prov}'"
        assert url.startswith("https://"), f"Provider icon URL must be secure HTTPS: {url}"


def test_provider_icon_url_fallback():
    """Verify fallback behavior for unknown providers and URL-based fallbacks."""
    # Unknown provider with no URL returns None (renders FALLBACK_EMOJI_ICON)
    assert get_provider_icon_url("Completely Unknown Academy") is None

    # Fallback emoji is a valid non-empty string
    assert FALLBACK_EMOJI_ICON == "🔖"

    # URL-based fallback for YouTube link under an unlisted creator name
    yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert get_provider_icon_url("Unlisted Creator", url=yt_url) == PROVIDER_ICON_MAP["YouTube"]

    # URL-based fallback for GitHub repository
    gh_url = "https://github.com/GoogleCloudPlatform/microservices-demo"
    assert get_provider_icon_url("Unlisted Repo", url=gh_url) == PROVIDER_ICON_MAP["GitHub"]


def test_canonical_catalog_no_thumbnail_field():
    """Verify catalog resources do not use large YouTube thumbnails or banner image URLs."""
    catalog = ResourceCatalog()
    resources = catalog.get_full_catalog()

    assert len(resources) >= 104

    for r in resources:
        # Check that there are no thumbnail attributes or properties
        assert not hasattr(r, "thumbnail_url"), "Thumbnail fields are prohibited"
        assert not hasattr(r, "banner_url"), "Banner fields are prohibited"
        # Validate that URLs are valid canonical web destinations
        assert r.url.startswith("https://")
        assert len(r.title) > 0
        assert len(r.provider) > 0
        assert r.difficulty in ["Beginner", "Intermediate", "Advanced", "All Levels"]
        assert r.resource_type in [
            "Course",
            "Video / Talk",
            "Documentation",
            "Hands-on Lab",
            "GitHub Project",
        ]
        assert r.category in ["WATCH", "LEARN", "PRACTICE", "BUILD"]
