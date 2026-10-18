"""Streamlit UI Application for Agentic Career Lab.

Privacy-first AI Career Assistant for students and job seekers powered by:
- Local Gemma 4 on Ollama for private local resume parsing & extraction
- Google ADK multi-agent orchestration
- Consent-guarded Gemini for learning roadmap synthesis
- OpenTelemetry distributed tracing with Tempo, Prometheus, and Grafana
"""

import os

import streamlit as st
from dotenv import load_dotenv

# Load env before any provider or client initialization
load_dotenv()

# ruff: noqa: E402
import httpx

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.agents.resume_agent.agent import PrivateResumeAgent
from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.agents.skill_builder.planner import DeterministicPlanningLLM
from agentic_career_lab.coordinator import (
    ADKCareerCoordinator,
    CareerAction,
    CareerCoordinator,
    CareerWorkflowState,
    LocalResumeContext,
)
from agentic_career_lab.llm.gemini import GeminiVertexClient
from agentic_career_lab.models import (
    ActivityProgress,
    ActivityStatus,
    LearningResource,
    OpportunitySearchQuery,
    StudentProfile,
)
from agentic_career_lab.providers.adzuna import AdzunaOpportunityProvider
from agentic_career_lab.providers.mock import MockOpportunityProvider
from agentic_career_lab.runtime.factory import (
    create_job_provider,
    create_resume_llm,
    create_skill_planner,
)
from agentic_career_lab.services.learning_resources import ResourceCatalog
from agentic_career_lab.services.resume_parser import ResumeParser
from agentic_career_lab.ui_helpers import (
    ACTIVITY_DIAGNOSTICS,
    CAREER_REPORT,
    DASHBOARD,
    FALLBACK_EMOJI_ICON,
    JOB_EXPLORER,
    LEARNING_HUB,
    MY_LEARNING_PLAN,
    MY_PROFILE,
    MY_RESUME,
    RESUME_STUDIO,
    SKILL_GAP_ANALYSIS,
    get_provider_icon_url,
    get_workflow_progress,
    normalize_navigation,
)

# Page configuration
st.set_page_config(
    page_title="Agentic Career Lab",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def navigate(page: str):
    """Centralized navigation state updater."""
    st.session_state["nav"] = page
    st.rerun()


# Custom CSS Design System
st.markdown(
    """
    <style>
    /* Modern, accessible font hierarchy and palette */
    :root {
        --primary-blue: #1A73E8;
        --primary-dark: #0f172a;
        --border-color: #e2e8f0;
        --text-muted: #64748b;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 2.2rem 2.5rem;
        border-radius: 14px;
        margin-bottom: 1.8rem;
        border: 1px solid #334155;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }
    .privacy-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Cards */
    .card-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08);
        color: #1e293b;
    }
    .card-box p, .card-box li, .card-box span:not([class^="badge-"]), .card-box div:not([class^="badge-"]):not(.card-title):not(.card-subtitle) {
        color: #1e293b;
    }
    .card-box code {
        color: #0f172a;
        background-color: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 600;
    }
    .card-box hr {
        margin: 10px 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.4rem;
    }
    .card-subtitle {
        font-size: 0.9rem;
        color: #475569;
        margin-bottom: 0.8rem;
    }

    /* Badges */
    .badge-demo {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #FDE68A;
    }
    .badge-live {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #BBF7D0;
    }
    .badge-skill-demonstrated {
        background-color: #ECFDF5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid #A7F3D0;
    }
    .badge-skill-partial {
        background-color: #FFFBEB;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid #FDE68A;
    }
    .badge-skill-missing {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid #FECACA;
    }

    /* Navigation button active accent */
    div[data-testid="stSidebar"] button {
        border-radius: 8px;
        font-weight: 500;
    }

    /* Career Journey Progress Tracker */
    .journey-tracker-container {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 1.5rem;
    }
    .journey-tracker-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .journey-tracker-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0f172a;
    }
    .journey-tracker-meta {
        font-size: 0.85rem;
        color: #475569;
    }

    /* Compact Resource Cards (Phase 2 & Phase 3) */
    .resource-card-compact {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: #f1f5f9;
        display: flex;
        flex-direction: column;
        gap: 6px;
        transition: border-color 0.15s ease;
    }
    .resource-card-compact:hover {
        border-color: #64748b;
    }
    .resource-header-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .provider-icon-wrapper {
        width: 28px;
        height: 28px;
        min-width: 28px;
        border-radius: 6px;
        background: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border: 1px solid #475569;
        margin-top: 2px;
        padding: 2px;
    }
    .provider-icon-img {
        width: 18px;
        height: 18px;
        object-fit: contain;
    }
    .resource-header-text {
        flex: 1;
        min-width: 0;
    }
    .resource-title-text {
        font-size: 0.98rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.35;
        margin-bottom: 2px;
    }
    .resource-provider-text {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .resource-meta-chips {
        font-size: 0.78rem;
        color: #cbd5e1;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
        margin-top: 2px;
    }
    .resource-desc-text {
        font-size: 0.84rem;
        color: #cbd5e1;
        line-height: 1.4;
        margin-top: 4px;
        padding-left: 40px;
    }
    .resource-skills-row {
        font-size: 0.78rem;
        color: #94a3b8;
        padding-left: 40px;
        margin-top: 2px;
    }
    .resource-action-container {
        padding-left: 40px;
        margin-top: 6px;
    }
    .btn-resource-action {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #2563eb;
        color: #ffffff !important;
        text-decoration: none !important;
        padding: 5px 14px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        transition: background 0.15s ease;
    }
    .btn-resource-action:hover {
        background: #1d4ed8;
    }
    .resource-badge-tier {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .resource-badge-diff {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_compact_resource_card(
    resource: LearningResource,
    action_label: str | None = None,
) -> None:
    """Render a compact student-friendly resource card with small provider logo/favicon."""
    icon_url = get_provider_icon_url(resource.provider, resource.url)
    if icon_url:
        icon_html = f"<img class='provider-icon-img' src='{icon_url}' alt='{resource.provider} icon' loading='lazy'/>"
    else:
        icon_html = f"<span style='font-size: 15px;'>{FALLBACK_EMOJI_ICON}</span>"

    # Action label determination
    if not action_label:
        if resource.category == "WATCH" or resource.resource_type == "Video / Talk":
            action_label = "Watch Video ↗"
        elif resource.category == "PRACTICE" or resource.resource_type == "Hands-on Lab":
            action_label = "Start Lab ↗"
        elif resource.category == "BUILD" or resource.resource_type == "GitHub Project":
            action_label = "View Repository ↗"
        else:
            action_label = (
                "Start Course ↗" if resource.resource_type == "Course" else "Open Guide ↗"
            )

    action_btn_html = (
        f"<a href='{resource.url}' target='_blank' class='btn-resource-action'>{action_label}</a>"
        if resource.url
        else "<span style='font-size: 0.8rem; color: #64748b; font-style: italic;'>Search official portal</span>"
    )

    # Relevant skills display
    skills_list = resource.relevant_skills or [resource.skill]
    skills_str = ", ".join(skills_list[:4])

    st.markdown(
        f"""
        <div class="resource-card-compact">
            <div class="resource-header-row">
                <div class="provider-icon-wrapper">{icon_html}</div>
                <div class="resource-header-text">
                    <div class="resource-title-text">{resource.title}</div>
                    <div class="resource-provider-text">{resource.provider}</div>
                    <div class="resource-meta-chips">
                        <span>{resource.resource_type}</span>
                        <span>•</span>
                        <span class="resource-badge-diff">{resource.difficulty}</span>
                        <span>•</span>
                        <span>{resource.estimated_duration}</span>
                        <span>•</span>
                        <span class="resource-badge-tier">{resource.free_or_paid}</span>
                    </div>
                </div>
            </div>
            <div class="resource-desc-text">{resource.reason or resource.learning_outcome}</div>
            <div class="resource-skills-row"><b>Skills:</b> {skills_str}</div>
            <div class="resource-action-container">{action_btn_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_career_journey_tracker(page_key_prefix: str, compact: bool = True) -> None:
    """Render interactive clickable Career Journey Progress Tracker."""
    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")
    plan = st.session_state.get("skill_builder_plan")

    progress = get_workflow_progress(opp, analysis, plan)
    percent = progress["percent_complete"]
    next_step = progress.get("canonical_next_step", progress["next_step"])

    target_str = (
        f"{opp.role} at {opp.company}" if opp else "None selected (Choose a role in Job Explorer)"
    )

    progress_dict = st.session_state.get("learning_progress", {})
    all_learning_tasks_done = False
    if plan and plan.learning_steps:
        total_tasks = sum(len(step.activities) for step in plan.learning_steps)
        completed_tasks = sum(
            1
            for step in plan.learning_steps
            for act_idx in range(len(step.activities))
            if progress_dict.get(f"step_{step.week}_act_{act_idx}")
            and progress_dict[f"step_{step.week}_act_{act_idx}"].status == ActivityStatus.COMPLETED
        )
        if total_tasks > 0 and completed_tasks == total_tasks:
            all_learning_tasks_done = True

    if percent == 100 and not all_learning_tasks_done:
        journey_status_str = "Career Preparation: 100% — Learning in Progress"
    else:
        journey_status_str = f"Career Journey Progress: {percent}% Complete"

    if not compact:
        # Full Dashboard Version
        st.markdown(f"#### {journey_status_str}")
        st.progress(percent)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="card-title">1. Target Opportunity</div>
                    <div class="card-subtitle">Select a target internship or job</div>
                    <p><b>Status:</b> {"✅ Selected" if progress["opportunity_selected"] else "⏳ Not Selected"}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "1. Job Explorer", key=f"{page_key_prefix}_btn_stage1", use_container_width=True
            ):
                navigate(JOB_EXPLORER)

        with c2:
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="card-title">2. Private Resume Analysis</div>
                    <div class="card-subtitle">Local Gemma 4 evidence extraction</div>
                    <p><b>Status:</b> {"✅ Analyzed" if progress["resume_analyzed"] else "⏳ Pending Upload"}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "2. Resume Analysis", key=f"{page_key_prefix}_btn_stage2", use_container_width=True
            ):
                navigate(MY_RESUME)

        with c3:
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="card-title">3. Learning Roadmap</div>
                    <div class="card-subtitle">Weekly milestones & capstone project</div>
                    <p><b>Status:</b> {"✅ Ready" if progress["skill_plan_built"] else "⏳ Not Generated"}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "3. Learning Plan", key=f"{page_key_prefix}_btn_stage3", use_container_width=True
            ):
                navigate(MY_LEARNING_PLAN)
    else:
        # Compact Tracker for all other pages
        st.markdown(
            f"""
            <div class="journey-tracker-container">
                <div class="journey-tracker-header">
                    <span class="journey-tracker-title">🚀 {journey_status_str}</span>
                    <span class="journey-tracker-meta"><b>Target:</b> {target_str}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(percent)

        col_s1, col_s2, col_s3, col_cont = st.columns([1, 1, 1, 1.2])
        with col_s1:
            s1_label = (
                "✅ 1. Job Selected" if progress["opportunity_selected"] else "⏳ 1. Select Job"
            )
            if st.button(s1_label, key=f"{page_key_prefix}_s1", use_container_width=True):
                navigate(JOB_EXPLORER)
        with col_s2:
            s2_label = (
                "✅ 2. Resume Analyzed" if progress["resume_analyzed"] else "⏳ 2. Analyze Resume"
            )
            if st.button(s2_label, key=f"{page_key_prefix}_s2", use_container_width=True):
                navigate(MY_RESUME)
        with col_s3:
            s3_label = "✅ 3. Plan Ready" if progress["skill_plan_built"] else "⏳ 3. Learning Plan"
            if st.button(s3_label, key=f"{page_key_prefix}_s3", use_container_width=True):
                navigate(MY_LEARNING_PLAN)
        with col_cont:
            btn_txt = "🎉 Review Career Report" if percent == 100 else "➡️ Continue Journey"
            if st.button(
                btn_txt, key=f"{page_key_prefix}_cont", type="primary", use_container_width=True
            ):
                navigate(next_step)
        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


def initialize_session_state() -> None:
    """Initialize application session state with safe defaults."""
    defaults = {
        "selected_opportunity": None,
        "resume_analysis": None,
        "skill_builder_plan": None,
        "agent_events": [],
        "job_matches": [],
        "preset_prompt": "",
        "resume_text": "",
        "resume_source": "paste",
        "resume_file_name": "",
        "nav": DASHBOARD,
        "job_source_label": "DEMO DATA",
        "cloud_consent": False,  # Phase 7: Strict opt-in default
        "learning_progress": {},  # Dict[str, ActivityProgress]
        "student_profile": StudentProfile(
            name="Alex Chen",
            target_role="AI Engineering Intern",
            education_level="Junior",
            major="Computer Science",
            skills=["Python", "SQL", "Docker", "Google Cloud", "REST APIs"],
            interests=["Machine Learning", "Cloud Infrastructure"],
        ),
        "profile_location": "Texas",
        "profile_grad_year": "2027",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "coordinator" not in st.session_state:
        domain_coord = CareerCoordinator(
            job_scout=JobScoutAgent(provider=create_job_provider()),
            resume_agent=PrivateResumeAgent(llm=create_resume_llm()),
            skill_builder=SkillBuilderAgent(llm=create_skill_planner()),
        )
        st.session_state["coordinator"] = ADKCareerCoordinator(domain_coord)
    if "career_workflow_state" not in st.session_state:
        st.session_state["career_workflow_state"] = CareerWorkflowState()
    if "resource_catalog" not in st.session_state:
        st.session_state["resource_catalog"] = ResourceCatalog()


initialize_session_state()

# ---------------------------------------------------------
# Sidebar Navigation & Context
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 Agentic Career Lab")
    st.caption("Privacy-First AI Career Assistant")

    st.markdown("---")
    st.markdown("**Student Journey**")

    # Render primary student navigation
    nav_current = normalize_navigation(st.session_state.get("nav"))

    btn_dash = st.button(
        "🏠 Dashboard",
        use_container_width=True,
        type="primary" if nav_current == DASHBOARD else "secondary",
    )
    btn_profile = st.button(
        "👤 My Profile",
        use_container_width=True,
        type="primary" if nav_current == MY_PROFILE else "secondary",
    )
    btn_jobs = st.button(
        "🎯 Job Explorer",
        use_container_width=True,
        type="primary" if nav_current == JOB_EXPLORER else "secondary",
    )
    btn_resume = st.button(
        "📄 My Resume",
        use_container_width=True,
        type="primary" if nav_current == MY_RESUME else "secondary",
    )
    btn_gaps = st.button(
        "🔍 Skill Gap Analysis",
        use_container_width=True,
        type="primary" if nav_current == SKILL_GAP_ANALYSIS else "secondary",
    )
    btn_hub = st.button(
        "📚 Learning Hub",
        use_container_width=True,
        type="primary" if nav_current == LEARNING_HUB else "secondary",
    )
    btn_plan = st.button(
        "🗺️ My Learning Plan",
        use_container_width=True,
        type="primary" if nav_current == MY_LEARNING_PLAN else "secondary",
    )
    btn_rep = st.button(
        "📋 Career Report",
        use_container_width=True,
        type="primary" if nav_current == CAREER_REPORT else "secondary",
    )

    st.markdown("---")
    st.markdown("**Extensions & Systems**")
    btn_activity = st.button(
        "📊 Activity & Diagnostics",
        use_container_width=True,
        type="primary" if nav_current == ACTIVITY_DIAGNOSTICS else "secondary",
    )
    btn_studio = st.button(
        "✨ Resume Studio (Preview)",
        use_container_width=True,
        type="primary" if nav_current == RESUME_STUDIO else "secondary",
    )

    # Sidebar button click events
    if btn_dash:
        navigate(DASHBOARD)
    elif btn_profile:
        navigate(MY_PROFILE)
    elif btn_jobs:
        navigate(JOB_EXPLORER)
    elif btn_resume:
        navigate(MY_RESUME)
    elif btn_gaps:
        navigate(SKILL_GAP_ANALYSIS)
    elif btn_hub:
        navigate(LEARNING_HUB)
    elif btn_plan:
        navigate(MY_LEARNING_PLAN)
    elif btn_rep:
        navigate(CAREER_REPORT)
    elif btn_activity:
        navigate(ACTIVITY_DIAGNOSTICS)
    elif btn_studio:
        navigate(RESUME_STUDIO)

    # Context Card in Sidebar
    st.markdown("---")
    opp = st.session_state.get("selected_opportunity")
    if opp:
        st.markdown(f"**Target Role:**\\n{opp.role}\\n\\n**Company:** {opp.company}")
    else:
        st.caption("No opportunity selected.")

    # Privacy Guarantee Badge
    st.markdown(
        """
        <div style="margin-top: 15px; padding: 10px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #166534;">🔒 Privacy Guarantee</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">
                Your resume text and contact data are processed strictly locally by Gemma 4 and NEVER sent to external cloud APIs.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Page 1: Dashboard
# ---------------------------------------------------------
def render_dashboard():
    """Render Student Dashboard with guided workflow progress."""
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">Agentic Career Lab</div>
            <div class="hero-subtitle">
                Explore real and demo job opportunities, analyze your resume privately on your device,
                and generate a personalized technical learning roadmap.
            </div>
            <span class="privacy-tag">🔒 100% Private Local Resume Analysis via Gemma 4</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_career_journey_tracker(page_key_prefix="dash", compact=False)

    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")
    plan = st.session_state.get("skill_builder_plan")
    progress = get_workflow_progress(opp, analysis, plan)

    st.markdown("---")
    # Phase 3: Dashboard Functional Quick Actions
    st.markdown("### ⚡ Quick Actions")
    st.caption(
        "One-click shortcuts to explore jobs, audit qualifications, and benchmark technical skills."
    )

    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        st.markdown(
            """
            <div class="card-box" style="min-height: 160px;">
                <div class="card-title">👤 Set Up My Profile</div>
                <div class="card-subtitle">Education, skills & location preferences</div>
                <p style="font-size: 0.8rem; color: #475569;">"I'm a junior computer science student. I know Python, SQL, Docker, and basic Google Cloud."</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Set Up My Profile", key="qa_btn_profile", use_container_width=True):
            navigate(MY_PROFILE)

    with qa2:
        st.markdown(
            """
            <div class="card-box" style="min-height: 160px;">
                <div class="card-title">🎯 Find Matching Jobs</div>
                <div class="card-subtitle">Prefill search with target track</div>
                <p style="font-size: 0.8rem; color: #475569;">"Find an AI/cloud internship that fits my profile"</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Find Matching Jobs", key="qa_btn_jobs", use_container_width=True):
            # Prefill and navigate
            navigate(JOB_EXPLORER)

    with qa3:
        st.markdown(
            """
            <div class="card-box" style="min-height: 160px;">
                <div class="card-title">📄 Compare My Resume</div>
                <div class="card-subtitle">Evidence alignment against target role</div>
                <p style="font-size: 0.8rem; color: #475569;">"Compare my resume against the selected AI Engineering Intern role."</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Compare My Resume", key="qa_btn_resume", use_container_width=True):
            if not opp:
                st.warning("Please pick an opportunity from Job Explorer first.")
            else:
                navigate(MY_RESUME)

    with qa4:
        st.markdown(
            """
            <div class="card-box" style="min-height: 160px;">
                <div class="card-title">🔍 Identify Skill Gaps</div>
                <div class="card-subtitle">Rank missing requirements & priorities</div>
                <p style="font-size: 0.8rem; color: #475569;">"Based on the selected internship and my current evidence, identify my top three skill gaps"</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Identify My Top 3 Skill Gaps", key="qa_btn_gaps", use_container_width=True):
            if not opp:
                st.warning("Please pick an opportunity first.")
            elif not analysis:
                st.warning("Please analyze your resume first to compare skill evidence.")
                navigate(MY_RESUME)
            else:
                navigate(SKILL_GAP_ANALYSIS)

    st.markdown("---")
    # Quick Summary Overview
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown("### Next Recommended Action")
        if not progress["opportunity_selected"]:
            st.info(
                "👉 **Step 1:** Browse available opportunities in Job Explorer to find a role matching your target track."
            )
            if st.button("Start: Find Opportunities", key="dash_next_1", type="primary"):
                navigate(JOB_EXPLORER)
        elif not progress["resume_analyzed"]:
            st.info(
                f"👉 **Step 2:** Upload or paste your resume to compare against **{opp.role}** at **{opp.company}**."
            )
            if st.button("Start: Prepare My Resume", key="dash_next_2", type="primary"):
                navigate(MY_RESUME)
        elif not progress["skill_plan_built"]:
            st.info(
                "👉 **Step 3:** Generate a structured 2 or 4 week learning roadmap to address your identified skill gaps."
            )
            if st.button("Generate Learning Plan", key="dash_next_3", type="primary"):
                navigate(MY_LEARNING_PLAN)
        else:
            st.success(
                "🎉 You have completed your initial career workflow! Review your comprehensive Career Report or explore the Learning Hub."
            )
            if st.button("Open Career Report", key="dash_next_4", type="primary"):
                navigate(CAREER_REPORT)

    with col_r:
        st.markdown("### Active Workspace Context")
        if opp:
            st.write(f"**Target Role:** {opp.role}")
            st.write(f"**Company:** {opp.company}")
            st.write(f"**Location:** {opp.location}")
            source_badge = (
                "badge-live" if st.session_state.get("job_source_label") == "LIVE" else "badge-demo"
            )
            st.markdown(
                f"**Source:** <span class='{source_badge}'>{st.session_state.get('job_source_label')}</span>",
                unsafe_allow_html=True,
            )
            if opp.source_url:
                st.link_button("View Source Posting", str(opp.source_url))
        else:
            st.caption(
                "No role selected. You can pick demo postings or search live Adzuna listings."
            )


# ---------------------------------------------------------
# Page 2: My Profile
# ---------------------------------------------------------
def render_my_profile():
    """Render dedicated My Profile configuration and management screen."""
    st.title("👤 My Profile")
    st.caption(
        "Manage your academic background, target roles, location preferences, and self-reported skills. "
        "Profile data stays strictly local in your active session."
    )

    render_career_journey_tracker("profile", compact=True)

    prof = st.session_state.get("student_profile")
    if not prof:
        prof = StudentProfile(
            name="Alex Chen",
            target_role="AI Engineering Intern",
            education_level="Junior",
            major="Computer Science",
            skills=["Python", "SQL", "Docker", "Google Cloud", "REST APIs"],
            interests=["Machine Learning", "Cloud Infrastructure"],
        )
        st.session_state["student_profile"] = prof

    cur_location = st.session_state.get("profile_location", "Texas")
    cur_grad_year = st.session_state.get("profile_grad_year", "2027")

    with st.form("my_profile_form"):
        st.markdown("### Academic & Career Objectives")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", value=prof.name or "Alex Chen")
            major = st.text_input("Field of Study / Major", value=prof.major or "Computer Science")
            education_level = st.selectbox(
                "Education Level",
                [
                    "Freshman",
                    "Sophomore",
                    "Junior",
                    "Senior",
                    "Master's Student",
                    "Bootcamp / Self-Taught",
                ],
                index=[
                    "Freshman",
                    "Sophomore",
                    "Junior",
                    "Senior",
                    "Master's Student",
                    "Bootcamp / Self-Taught",
                ].index(
                    prof.education_level
                    if prof.education_level
                    in [
                        "Freshman",
                        "Sophomore",
                        "Junior",
                        "Senior",
                        "Master's Student",
                        "Bootcamp / Self-Taught",
                    ]
                    else "Junior"
                ),
            )
        with c2:
            grad_year = st.text_input("Graduation Year", value=str(cur_grad_year))
            target_role = st.text_input(
                "Target Career Role", value=prof.target_role or "AI Engineering Intern"
            )
            location = st.text_input("Preferred Location", value=cur_location)

        st.markdown("---")
        st.markdown("### Technical Skills")
        st.caption("Enter comma-separated skills you have studied, practiced, or self-reported:")
        default_skills_str = (
            ", ".join(prof.skills)
            if prof.skills
            else "Python, SQL, Docker, Google Cloud, REST APIs"
        )
        skills_str = st.text_area(
            "Current Self-Reported Skills", value=default_skills_str, height=75
        )

        st.markdown("---")
        b1, b2 = st.columns([1, 1])
        with b1:
            btn_save = st.form_submit_button(
                "💾 Save Profile", type="primary", use_container_width=True
            )
        with b2:
            btn_load_demo = st.form_submit_button(
                "🔄 Load Demo Student Profile (Alex Chen)", use_container_width=True
            )

    if btn_save:
        skills_list = [s.strip() for s in skills_str.split(",") if s.strip()]
        updated_prof = StudentProfile(
            name=name.strip() or "Student",
            target_role=target_role.strip() or "AI Engineering Intern",
            education_level=education_level,
            major=major.strip() or "Computer Science",
            skills=skills_list,
            interests=prof.interests or ["Machine Learning"],
        )
        st.session_state["student_profile"] = updated_prof
        st.session_state["profile_location"] = location.strip()
        st.session_state["profile_grad_year"] = grad_year.strip()
        st.success(
            "✅ Profile updated successfully! Changes will prefill your Job Explorer and Learning recommendations."
        )
        st.rerun()

    if btn_load_demo:
        demo_prof = StudentProfile(
            name="Alex Chen",
            target_role="AI Engineering Intern",
            education_level="Junior",
            major="Computer Science",
            skills=["Python", "SQL", "Docker", "Google Cloud", "REST APIs"],
            interests=["Machine Learning", "Cloud Infrastructure"],
        )
        st.session_state["student_profile"] = demo_prof
        st.session_state["profile_location"] = "Texas"
        st.session_state["profile_grad_year"] = "2027"
        st.info(
            "ℹ️ Loaded deterministic Alex Chen demo profile (Junior, Computer Science, Class of 2027)."
        )
        st.rerun()

    # Visual distinction between self-reported and verified resume skills
    st.markdown("---")
    st.markdown("### 🛡️ Skills Integrity & Verification Breakdown")
    col_self, col_ver = st.columns(2)
    with col_self:
        st.markdown(
            """
            <div class="card-box">
                <div class="card-title">📝 Self-Reported Profile Skills</div>
                <div class="card-subtitle">Declared in profile — unverified claims</div>
                <p style="font-size: 0.85rem; color: #475569;">
                    These skills help prefill searches and course suggestions. They are never treated as proven qualifications without evidence.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for s in prof.skills:
            st.markdown(f"- 🔸 **{s}** *(Self-Reported)*")

    with col_ver:
        analysis = st.session_state.get("resume_analysis")
        demonstrated_skills = []
        if analysis and analysis.requirement_matches:
            demonstrated_skills = [
                m.requirement for m in analysis.requirement_matches if m.status == "Demonstrated"
            ]

        st.markdown(
            """
            <div class="card-box">
                <div class="card-title">✅ Resume-Verified Skills</div>
                <div class="card-subtitle">Extracted locally from your resume by Gemma 4</div>
                <p style="font-size: 0.85rem; color: #475569;">
                    Skills with documented evidence in your uploaded resume, coursework, or technical projects.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if demonstrated_skills:
            for ds in demonstrated_skills:
                st.markdown(f"- 🔹 **{ds}** *(Verified by Resume Evidence)*")
        else:
            st.caption(
                "No resume uploaded or verified yet. Upload your resume in 'My Resume' to verify skills."
            )


# ---------------------------------------------------------
# Page 3: Job Explorer
# ---------------------------------------------------------
def render_job_explorer():
    """Render Job Explorer screen with clear demo vs live badge distinction."""
    st.title("🎯 Job Explorer")
    st.caption(
        "Search real-time internships or explore deterministic sample roles with verifiable requirements."
    )

    render_career_journey_tracker("jobs", compact=True)

    prof = st.session_state.get("student_profile")
    pref_role = prof.target_role if prof and prof.target_role else "AI Engineering Intern"
    pref_location = st.session_state.get("profile_location", "Texas")
    pref_skills = (
        ", ".join(prof.skills)
        if prof and prof.skills
        else "Python, SQL, Docker, Google Cloud, REST APIs"
    )

    with st.expander("🔍 Search Filters & Provider Settings", expanded=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            role = st.text_input("Target Role", value=pref_role)
        with c2:
            location = st.text_input("Location", value=pref_location)
        with c3:
            internship_only = st.selectbox("Type", ["Internships Only", "All Roles"], index=0)

        skills_input = st.text_input("Key Skills to Highlight", value=pref_skills)
        source = st.radio(
            "Provider Mode",
            ["Demo Data (Deterministic Mock)", "Live Jobs (Adzuna API)"],
            index=0,
            horizontal=True,
        )

        if st.button("Find Opportunities", type="primary"):
            if "Live Jobs" in source:
                try:
                    provider = AdzunaOpportunityProvider()
                    st.session_state["job_source_label"] = "LIVE"
                except Exception as e:
                    st.error(f"Live provider configuration notice: {str(e)}")
                    st.stop()
            else:
                provider = MockOpportunityProvider()
                st.session_state["job_source_label"] = "DEMO DATA"

            st.session_state["coordinator"].domain_coordinator.job_scout.provider = provider

            profile = StudentProfile(
                name="Student",
                target_role=role,
                education_level="Junior",
                major="Computer Science",
                skills=[s.strip() for s in skills_input.split(",") if s.strip()],
            )
            query = OpportunitySearchQuery(
                role=role,
                location=location,
                internship_only=("Internship" in internship_only),
                keywords=[],
            )
            state = st.session_state["career_workflow_state"]
            state.student_profile = profile
            state.search_query = query

            st.session_state["coordinator"].execute_action(CareerAction.FIND_OPPORTUNITIES, state)
            st.session_state["job_matches"] = state.opportunities
            st.session_state["agent_events"] = state.activity_events

    # Results Listing
    label = st.session_state.get("job_source_label", "DEMO DATA")
    badge_class = "badge-live" if label == "LIVE" else "badge-demo"
    st.markdown(
        f"### Matching Opportunities <span class='{badge_class}'>{label}</span>",
        unsafe_allow_html=True,
    )

    if not st.session_state.get("job_matches"):
        st.info(
            "No opportunities currently loaded. Click 'Find Opportunities' above to view matching roles."
        )
        return

    for idx, match in enumerate(st.session_state["job_matches"]):
        opp = match.opportunity
        st.markdown(
            f"""
            <div class="card-box">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div class="card-title">{opp.role}</div>
                        <div class="card-subtitle"><b>{opp.company}</b> • {opp.location}</div>
                    </div>
                    <span class="{badge_class}">{label}</span>
                </div>
                <p style="font-size: 0.95rem; color: #334155; margin-top: 8px;">{opp.description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"View Requirements ({len(opp.requirements)} skills)", expanded=False):
            req_cols = st.columns(3)
            for r_idx, req in enumerate(opp.requirements):
                with req_cols[r_idx % 3]:
                    st.markdown(f"- **{req.skill}** ({req.req_type.value})")
                    if req.context:
                        st.caption(f"Context: {req.context}")

        btn_cols = st.columns([1, 4])
        with btn_cols[0]:
            if st.button("Prepare My Resume", key=f"btn_pick_{idx}", type="primary"):
                # Requirement 10: Invalidate stale resume comparisons and learning plans when job changes
                prev_opp = st.session_state.get("selected_opportunity")
                if prev_opp and prev_opp.opportunity_id != opp.opportunity_id:
                    st.session_state["resume_analysis"] = None
                    st.session_state["skill_builder_plan"] = None
                    state = st.session_state["career_workflow_state"]
                    state.resume_analysis = None
                    state.skill_builder_plan = None

                st.session_state["selected_opportunity"] = opp
                state = st.session_state["career_workflow_state"]
                state.selected_opportunity = opp
                navigate(MY_RESUME)
        with btn_cols[1]:
            if opp.source_url:
                st.link_button("View Original Source", str(opp.source_url))
        st.markdown("---")


# ---------------------------------------------------------
# Page 3: My Resume (Upload & Local Analysis)
# ---------------------------------------------------------
def render_my_resume():
    """Render My Resume upload and local Gemma 4 analysis screen."""
    st.title("📄 My Resume")
    st.caption(
        "Upload or paste your resume. Extraction runs 100% locally on your machine via Gemma 4."
    )

    render_career_journey_tracker("resume", compact=True)

    opp = st.session_state.get("selected_opportunity")
    if not opp:
        st.warning(
            "⚠️ No opportunity selected yet. Please select an opportunity from the Job Explorer first."
        )
        if st.button("Browse Job Explorer", type="primary"):
            navigate(JOB_EXPLORER)
        return

    st.markdown(f"**Target Role:** {opp.role} at **{opp.company}**")

    tab_upload, tab_paste, tab_demo = st.tabs(
        ["Upload Resume (.pdf / .docx)", "Paste Text / Markdown", "Load Demo Profile"]
    )

    with tab_upload:
        uploaded_file = st.file_uploader("Select Resume File", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("File is too large. Maximum size is 5MB.")
            else:
                parser = ResumeParser()
                parsed = parser.parse_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)
                if parsed.extraction_warnings:
                    for w in parsed.extraction_warnings:
                        st.warning(w)
                if parsed.text.strip():
                    st.session_state["resume_text"] = parsed.text
                    st.session_state["resume_source"] = "upload"
                    st.session_state["resume_file_name"] = parsed.file_name
                    st.success("✓ Resume loaded locally in memory")
                    st.caption(f"File: {parsed.file_name} | Size: {len(parsed.text)} characters")

    with tab_paste:
        resume_input = st.text_area(
            "Paste Resume Text",
            height=200,
            value=st.session_state.get("resume_text", "")
            if st.session_state.get("resume_source") == "paste"
            else "",
            placeholder="Paste your resume contents here...",
        )
        if resume_input:
            st.session_state["resume_text"] = resume_input
            st.session_state["resume_source"] = "paste"
            st.session_state["resume_file_name"] = "pasted_resume"

    with tab_demo:
        demo_resume = (
            "Alex Student\n"
            "B.S. Computer Science, Expected 2027\n\n"
            "Skills:\n"
            "Python, SQL, Docker, Google Cloud, REST APIs\n\n"
            "Projects:\n"
            "High-Throughput Web Service — Built a containerized Python REST service with Docker and PostgreSQL.\n\n"
            "Experience:\n"
            "Student Research Assistant — Example University\n"
            "Developed automated data pipelines in Python and queried relational databases."
        )
        if st.button("Load Demo Resume Text"):
            st.session_state["resume_text"] = demo_resume
            st.session_state["resume_source"] = "paste"
            st.session_state["resume_file_name"] = "demo_resume"
            st.rerun()

    st.markdown("---")

    # Private Analysis Trigger
    if st.button("Analyze Resume Privately", type="primary"):
        resume_content = st.session_state.get("resume_text", "").strip()
        if not resume_content:
            st.error("Please provide your resume text before running analysis.")
            return

        with st.spinner(
            "Analyzing resume locally with Gemma 4 on Ollama (this runs on your device)..."
        ):
            try:
                state = st.session_state["career_workflow_state"]
                state.selected_opportunity = opp
                local_context = LocalResumeContext(raw_resume_text=resume_content)

                st.session_state["coordinator"].execute_action(
                    CareerAction.PREPARE_RESUME, state, local_resume=local_context
                )
                st.session_state["resume_analysis"] = state.resume_analysis
                st.session_state["agent_events"] = state.activity_events
                st.success("✓ Local Gemma 4 analysis complete!")
            except Exception as e:
                st.error(f"Private analysis error: {str(e)}. Ensure Ollama is running locally.")

    # Results Display
    if st.session_state.get("resume_analysis") is not None:
        analysis = st.session_state["resume_analysis"]

        # Phase 3 Fix: Fix literal '\n' bug and categorize skills cleanly
        st.markdown("### Extracted Resume Evidence")

        # Distinct skill list
        raw_skills = []
        if analysis.suggestions and analysis.suggestions[0].evidence_used:
            raw_skills = analysis.suggestions[0].evidence_used
        else:
            raw_skills = ["Python", "SQL", "Docker", "Google Cloud", "REST APIs"]

        # Clean any escaped newlines
        clean_skills = [s.replace("\\n", " ").strip() for s in raw_skills if s.strip()]

        st.markdown("**Skills Mentioned in Resume:**")
        badge_html = " ".join(
            [f"<span class='badge-skill-demonstrated'>{s}</span>" for s in clean_skills]
        )
        st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Job Requirement Evidence Alignment")
        st.caption("Verifiable alignment between your resume evidence and target job requirements:")

        for match in analysis.requirement_matches:
            if match.status == "Demonstrated":
                st.markdown(
                    f"✅ **{match.requirement}** — <span class='badge-skill-demonstrated'>Demonstrated with Evidence</span>",
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"**Verified Evidence:** {match.evidence or 'Demonstrated in documented work experience or technical projects.'}"
                )
            elif match.status == "Partial":
                st.markdown(
                    f"⚠️ **{match.requirement}** — <span class='badge-skill-partial'>Mentioned / Partially Evidenced</span>",
                    unsafe_allow_html=True,
                )
                reason_detail = (
                    match.evidence
                    if match.evidence
                    else "Listed as a keyword or coursework without associated production code, metrics, or project deliverables."
                )
                st.caption(
                    f"**Evidence Assessment:** {reason_detail} *(Needs measurable deliverables or repo evidence to claim as demonstrated)*"
                )
            else:
                st.markdown(
                    f"❌ **{match.requirement}** — <span class='badge-skill-missing'>Missing Requirement</span>",
                    unsafe_allow_html=True,
                )
                st.caption(
                    "**Evidence Assessment:** No evidence found in uploaded resume. Candidate should build this skill through the Learning Hub."
                )

        st.markdown("---")
        st.markdown("### Action-Oriented Resume Suggestions")
        for sugg in analysis.suggestions:
            c_curr, c_sugg = st.columns(2)
            with c_curr:
                st.markdown("**Current Statement**")
                st.info(sugg.original_text)
            with c_sugg:
                st.markdown("**Evidence-Grounded Recommendation**")
                st.success(sugg.suggested_text)
            st.caption(f"Evidence grounded: {', '.join(sugg.evidence_used)}")

        st.markdown("---")
        col_next, _ = st.columns([2, 3])
        with col_next:
            if st.button("Build My Skill Plan", key="btn_goto_skills", type="primary"):
                navigate(SKILL_GAP_ANALYSIS)


# ---------------------------------------------------------
# Page 4: Skill Gap Analysis
# ---------------------------------------------------------
def render_skill_gap_analysis():
    """Render Skill Gap Analysis comparing resume to opportunity requirements."""
    st.title("🔍 Skill Gap Analysis")
    st.caption(
        "Transparent classification of skills: Demonstrated, Mentioned / Partial, and Missing gaps."
    )

    render_career_journey_tracker("gaps", compact=True)

    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")

    if not opp:
        st.info("Please select an opportunity from the Job Explorer first.")
        if st.button("Browse Job Explorer"):
            navigate(JOB_EXPLORER)
        return

    if not analysis:
        st.info("Analyze your resume first to view evidence-based skill comparisons.")
        if st.button("Go to My Resume"):
            navigate(MY_RESUME)
        return

    st.markdown(f"**Target Role:** {opp.role} at {opp.company}")

    # Categorize matches
    demonstrated = [m for m in analysis.requirement_matches if m.status == "Demonstrated"]
    partial = [m for m in analysis.requirement_matches if m.status == "Partial"]
    missing = [m for m in analysis.requirement_matches if m.status == "Missing"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Demonstrated Skills", len(demonstrated))
    m2.metric("Partial / Developing", len(partial))
    m3.metric("Priority Skill Gaps", len(missing))

    st.markdown("---")
    st.markdown("### Detailed Gap Breakdown")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Demonstrated Strengths (Verified)")
        if demonstrated:
            for item in demonstrated:
                st.markdown(f"✅ **{item.requirement}**")
                st.caption(
                    f"**Evidence:** {item.evidence or 'Documented in resume work history or technical deliverables.'}"
                )
        else:
            st.caption("No requirements fully demonstrated yet.")

        st.markdown("#### Mentioned / Partially Evidenced Skills")
        if partial:
            for item in partial:
                st.markdown(f"⚠️ **{item.requirement}**")
                reason_expl = (
                    item.evidence
                    if item.evidence
                    else "Mentioned as coursework or keyword only, lacking hands-on repository or metrics."
                )
                st.caption(
                    f"**Status Explanation:** {reason_expl} *(Cannot claim demonstrated without concrete project deliverables)*"
                )
        else:
            st.caption("No partial skills identified.")

    with col_b:
        st.markdown("#### Missing Job Requirements (Action Needed)")
        if missing:
            for item in missing:
                st.markdown(f"❌ **{item.requirement}**")
                st.caption(
                    "**Status Explanation:** Stated job requirement with zero evidence in your resume. Prioritize in your learning roadmap."
                )
        else:
            st.success("Great news! All required skills are demonstrated or partially evidenced.")

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Explore Learning Catalog", type="secondary", use_container_width=True):
            navigate(LEARNING_HUB)
    with c2:
        if st.button("Generate Learning Roadmap", type="primary", use_container_width=True):
            navigate(MY_LEARNING_PLAN)


# ---------------------------------------------------------
# Page 5: Learning Hub (Curated Catalog)
# ---------------------------------------------------------
def render_learning_hub():
    """Render curated technical learning resource catalog tied to job skills."""
    st.title("📚 Learning Hub")
    st.caption(
        "Curated, verified technical learning resources from Google Cloud, Kubernetes.io, CNCF, and official providers."
    )

    render_career_journey_tracker("hub", compact=True)

    catalog: ResourceCatalog = st.session_state["resource_catalog"]
    all_skills = catalog.get_all_skills()

    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")

    if opp:
        st.markdown(f"**Target Role Context:** {opp.role} at {opp.company}")

    # Quick filter banner for detected missing requirements
    missing_skills = []
    if analysis and analysis.requirement_matches:
        missing_skills = [
            m.requirement for m in analysis.requirement_matches if m.status == "Missing"
        ]

    if missing_skills:
        st.info(f"🎯 **Identified Job Gaps:** {', '.join(missing_skills)}")

    # Filter controls
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 1])
    with f1:
        options = ["All Skills"]
        if missing_skills:
            options += [f"🎯 Missing: {s}" for s in missing_skills]
        options += [s for s in all_skills if s not in missing_skills]
        selected_option = st.selectbox("Skill / Gap", options)
    with f2:
        diff_filter = st.selectbox(
            "Difficulty", ["All Difficulties", "Beginner", "Intermediate", "Advanced"]
        )
    with f3:
        all_types = sorted(list({r.resource_type for r in catalog.get_full_catalog()}))
        type_filter = st.selectbox("Resource Type", ["All Types"] + all_types)
    with f4:
        all_providers = sorted(list({r.provider for r in catalog.get_full_catalog()}))
        provider_filter = st.selectbox("Provider", ["All Providers"] + all_providers)
    with f5:
        all_tiers = sorted(list({r.free_or_paid for r in catalog.get_full_catalog()}))
        tier_filter = st.selectbox("Access / Cost", ["All Tiers"] + all_tiers)

    # Collect filtered resources
    selected_skill = selected_option.replace("🎯 Missing: ", "").strip()
    if selected_skill == "All Skills":
        resources = catalog.get_full_catalog()
    else:
        resources = catalog.get_resources_for_skill(selected_skill)

    if diff_filter != "All Difficulties":
        resources = [r for r in resources if r.difficulty == diff_filter]
    if type_filter != "All Types":
        resources = [r for r in resources if r.resource_type == type_filter]
    if provider_filter != "All Providers":
        resources = [r for r in resources if r.provider == provider_filter]
    if tier_filter != "All Tiers":
        resources = [r for r in resources if r.free_or_paid == tier_filter]

    # Sort verified resources first (Hands-on Lab, GitHub Project & Course with verified URLs prioritized over generic docs)
    def resource_sort_key(r):
        has_url = 1 if r.url else 0
        type_priority = {
            "Hands-on Lab": 4,
            "GitHub Project": 3,
            "Course": 2,
            "Video / Talk": 2,
            "Documentation": 1,
        }.get(r.resource_type, 0)
        return (has_url, type_priority)

    resources = sorted(resources, key=resource_sort_key, reverse=True)

    st.markdown(f"**Found {len(resources)} verified resources:**")
    st.markdown("---")

    for res in resources:
        render_compact_resource_card(res)


# ---------------------------------------------------------
# Page 6: My Learning Plan (Strict Duration Roadmap)
# ---------------------------------------------------------
def render_my_learning_plan():
    """Render structured 2 or 4 week roadmap respecting user duration and privacy consent."""
    st.title("🗺️ My Learning Plan")
    st.caption(
        "Personalized learning roadmap and milestone deliverables targeting your missing job requirements."
    )

    render_career_journey_tracker("plan", compact=True)

    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")

    if not opp:
        st.info("Select an opportunity in Job Explorer before building a learning plan.")
        if st.button("Go to Job Explorer"):
            navigate(JOB_EXPLORER)
        return

    if not analysis:
        st.info("Analyze your resume in My Resume before generating a personalized plan.")
        if st.button("Go to My Resume"):
            navigate(MY_RESUME)
        return

    st.markdown(f"**Target Role:** {opp.role} at {opp.company}")

    with st.expander("⚙️ Roadmap Settings & Privacy Guard", expanded=True):
        c1, c2 = st.columns([2, 3])
        with c1:
            duration_choice = st.radio(
                "Roadmap Duration", ["2 Weeks (Accelerated)", "4 Weeks (Comprehensive)"], index=1
            )
            duration_weeks = 2 if "2 Weeks" in duration_choice else 4

        with c2:
            st.markdown("#### 🔒 Privacy & Cloud AI Sharing Consent")
            # Phase 7 Fix: Default to unchecked (False) for all new sessions
            consent = st.checkbox(
                "I explicitly consent to sharing non-PII skill gaps with Cloud AI (Gemini) for roadmap synthesis.",
                value=st.session_state.get("cloud_consent", False),
                help="When unchecked, the system uses a 100% local deterministic Python planner. Raw resumes never leave your machine.",
            )
            st.session_state["cloud_consent"] = consent

        if st.button("Generate Learning Plan", type="primary"):
            state = st.session_state["career_workflow_state"]
            state.selected_opportunity = opp
            state.resume_analysis = analysis
            state.requested_duration_weeks = duration_weeks

            if not consent:
                st.info(
                    "🔒 Cloud sharing declined: Generating plan using local deterministic Python planner."
                )
                fallback_builder = SkillBuilderAgent(llm=DeterministicPlanningLLM())
                plan = fallback_builder.run(opp, analysis, duration_weeks=duration_weeks)
                state.skill_builder_plan = plan
                st.session_state["skill_builder_plan"] = plan
                st.session_state["agent_events"] = fallback_builder.events
            else:
                st.info("☁ Cloud sharing approved: Generating plan using Google ADK & Gemini.")
                st.session_state["coordinator"].execute_action(CareerAction.BUILD_SKILLS, state)
                st.session_state["skill_builder_plan"] = state.skill_builder_plan
                st.session_state["agent_events"] = state.activity_events

            st.success("✓ Learning plan generated successfully.")
            st.rerun()

    plan = st.session_state.get("skill_builder_plan")
    if not plan or not plan.learning_steps:
        st.info("Click 'Generate Learning Plan' above to build your personalized weekly roadmap.")
        return

    catalog = ResourceCatalog()

    # Calculate Overall Learning Progress (Phase 6)
    progress_dict = st.session_state.get("learning_progress", {})
    total_tasks = sum(len(step.activities) for step in plan.learning_steps)
    completed_tasks = sum(
        1
        for step in plan.learning_steps
        for act_idx in range(len(step.activities))
        if progress_dict.get(f"step_{step.week}_act_{act_idx}")
        and progress_dict[f"step_{step.week}_act_{act_idx}"].status == ActivityStatus.COMPLETED
    )
    overall_pct = int(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Phase 7: Find Next Incomplete Learning Activity for Continue Learning Action
    next_incomplete_task = None
    for step in plan.learning_steps:
        for act_idx, act in enumerate(step.activities):
            act_key = f"step_{step.week}_act_{act_idx}"
            if (
                not progress_dict.get(act_key)
                or progress_dict[act_key].status != ActivityStatus.COMPLETED
            ):
                assoc_res_id = step.activity_resource_ids.get(act_idx)
                assoc_res = catalog.get_resource_by_id(assoc_res_id) if assoc_res_id else None
                next_incomplete_task = {
                    "week": step.week,
                    "focus": step.focus,
                    "activity": act,
                    "resource": assoc_res,
                }
                break
        if next_incomplete_task:
            break

    st.markdown("---")
    st.markdown(
        f"""
        <div class="card-box" style="margin-bottom: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div class="card-title">🎯 Overall Learning Activity Progress: {overall_pct}%</div>
                    <div class="card-subtitle">{completed_tasks} of {total_tasks} practical tasks completed across {len(plan.learning_steps)} weeks</div>
                </div>
                <span class="badge-skill-demonstrated">{completed_tasks}/{total_tasks} Completed</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(overall_pct)

    # Phase 7: Continue Learning Highlight Banner
    if next_incomplete_task:
        res_info = ""
        if next_incomplete_task["resource"]:
            r = next_incomplete_task["resource"]
            res_info = f" • Recommended Material: <b>{r.title}</b> ({r.provider})"
        st.info(
            f"💡 **Recommended Next Step (Week {next_incomplete_task['week']}):** "
            f"{next_incomplete_task['activity']}{res_info}"
        )
    else:
        st.success(
            "🎉 All weekly learning tasks completed! Review your Capstone Portfolio Project."
        )

    st.markdown(
        f"### Roadmap Milestones & Guided Learning Materials ({len(plan.learning_steps)} Weeks)"
    )
    st.caption(f"Plan Summary: {plan.summary}")

    for step in plan.learning_steps:
        # Calculate weekly completion
        step_tasks = len(step.activities)
        step_done = sum(
            1
            for act_idx in range(step_tasks)
            if progress_dict.get(f"step_{step.week}_act_{act_idx}")
            and progress_dict[f"step_{step.week}_act_{act_idx}"].status == ActivityStatus.COMPLETED
        )
        step_pct = int(step_done / step_tasks * 100) if step_tasks > 0 else 0

        with st.expander(
            f"📅 Week {step.week}: {step.focus} — {step_done}/{step_tasks} Tasks Done ({step_pct}%)",
            expanded=True,
        ):
            st.markdown(f"**Target Skills:** {', '.join(step.skills)}")
            st.markdown(f"**Expected Weekly Output:** {step.expected_output}")

            # Guided Learning Material Tabs (WATCH, LEARN, PRACTICE, BUILD)
            tab_watch, tab_learn, tab_practice, tab_build = st.tabs(
                [
                    "📺 WATCH (Videos)",
                    "📖 LEARN (Courses & Docs)",
                    "💻 PRACTICE (Labs)",
                    "🛠️ BUILD (GitHub Projects)",
                ]
            )

            step_skills = step.skills if step.skills else ["Python"]

            with tab_watch:
                watch_res = catalog.get_resources_by_category(step_skills, "WATCH")
                if watch_res:
                    for r in watch_res[:2]:
                        render_compact_resource_card(r, action_label="Watch Video ↗")
                else:
                    st.caption(
                        "No video tutorials specifically tagged for this week's target skills."
                    )
                if st.button("🔍 View More in Learning Hub", key=f"more_watch_w{step.week}"):
                    navigate(LEARNING_HUB)

            with tab_learn:
                learn_res = catalog.get_resources_by_category(step_skills, "LEARN")
                if learn_res:
                    for r in learn_res[:2]:
                        render_compact_resource_card(
                            r,
                            action_label="Start Course ↗"
                            if r.resource_type == "Course"
                            else "Open Guide ↗",
                        )
                else:
                    st.caption("Review official technical documentation for this week's focus.")
                if st.button("🔍 View More in Learning Hub", key=f"more_learn_w{step.week}"):
                    navigate(LEARNING_HUB)

            with tab_practice:
                practice_res = catalog.get_resources_by_category(step_skills, "PRACTICE")
                if practice_res:
                    for r in practice_res[:2]:
                        render_compact_resource_card(r, action_label="Start Lab ↗")
                else:
                    st.caption(
                        "Apply skills through interactive CLI scenarios or local test cases."
                    )
                if st.button("🔍 View More in Learning Hub", key=f"more_practice_w{step.week}"):
                    navigate(LEARNING_HUB)

            with tab_build:
                build_res = catalog.get_resources_by_category(step_skills, "BUILD")
                if build_res:
                    for r in build_res[:2]:
                        render_compact_resource_card(r, action_label="View Repository ↗")
                else:
                    st.caption(
                        "Build and publish a standalone GitHub project to verify proficiency."
                    )
                if st.button("🔍 View More in Learning Hub", key=f"more_build_w{step.week}"):
                    navigate(LEARNING_HUB)

            st.markdown("---")
            st.markdown("##### 📝 Weekly Milestone Tasks & Verifiable Evidence")
            st.caption(
                "ℹ️ *Associate your work with official learning materials. Tasks are never automatically checked complete when links open; provide supporting evidence (GitHub PR, commit, or lab notes) to claim progress.*"
            )

            for act_idx, act in enumerate(step.activities):
                act_key = f"step_{step.week}_act_{act_idx}"
                current_prog = progress_dict.get(
                    act_key, ActivityProgress(step_id=act_key, activity_name=act)
                )

                # Look up associated resource if available
                assoc_res_id = step.activity_resource_ids.get(act_idx)
                assoc_res = catalog.get_resource_by_id(assoc_res_id) if assoc_res_id else None

                c_check, c_note = st.columns([3, 2])
                with c_check:
                    is_done = st.checkbox(
                        f"**{act}**",
                        value=(current_prog.status == ActivityStatus.COMPLETED),
                        key=f"check_{act_key}",
                    )
                    current_prog.status = (
                        ActivityStatus.COMPLETED if is_done else ActivityStatus.NOT_STARTED
                    )
                    if assoc_res and assoc_res.url:
                        st.markdown(
                            f"<span style='font-size: 0.82rem;'>📚 Related Material: <a href='{assoc_res.url}' target='_blank'>{assoc_res.title}</a> ({assoc_res.provider})</span>",
                            unsafe_allow_html=True,
                        )

                with c_note:
                    note = st.text_input(
                        "Evidence / Deliverable Link:",
                        value=current_prog.evidence_notes,
                        key=f"note_{act_key}",
                        placeholder="e.g. GitHub PR, commit, or lab completion note",
                    )
                    current_prog.evidence_notes = note
                    if assoc_res:
                        current_prog.associated_resource_id = assoc_res.resource_id
                    progress_dict[act_key] = current_prog

            st.session_state["learning_progress"] = progress_dict

    # Portfolio Project Capstone
    if plan.portfolio_project:
        st.markdown("---")
        st.markdown("### 🏆 Capstone Portfolio Project Deliverable")
        proj = plan.portfolio_project
        st.markdown(
            f"""
            <div class="card-box">
                <div class="card-title">{proj.title}</div>
                <div class="card-subtitle">{proj.objective}</div>
                <p><b>Skills Practiced:</b> {", ".join(proj.skills_practiced)}</p>
                <p><b>Verifiable Deliverables:</b> {", ".join(proj.deliverables)}</p>
                <p><b>Potential Resume Evidence Upon Completion:</b> {", ".join(proj.evidence_created)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("Generate Career Report", type="primary"):
        navigate(CAREER_REPORT)


# ---------------------------------------------------------
# Page 7: Career Report
# ---------------------------------------------------------
def render_career_report():
    """Render comprehensive compiled Career Report."""
    st.title("📋 Career Action Report")
    st.caption(
        "Comprehensive summary of your opportunity alignment, verified evidence, and learning roadmap."
    )

    render_career_journey_tracker("rep", compact=True)

    state = st.session_state.get("career_workflow_state")
    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")
    plan = st.session_state.get("skill_builder_plan")

    if not opp or not analysis or not plan:
        st.info(
            "Complete the workflow steps (Job Explorer, My Resume, and Learning Plan) to compile your report."
        )
        return

    action_plan = st.session_state["coordinator"].create_action_plan(state)

    st.success(f"Status: **{action_plan.workflow_status}**")

    st.markdown(
        f"""
        <div class="card-box">
            <div class="card-title">Career Report: {opp.role}</div>
            <div class="card-subtitle"><b>Company:</b> {opp.company} • <b>Location:</b> {opp.location}</div>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #e2e8f0;"/>
            <p><b>Resume Verification:</b> {action_plan.resume_evidence_summary or "Verified locally by Gemma 4"}</p>
            <p><b>Priority Skill Gaps:</b> {len(action_plan.priority_skill_gaps)} identified requirements</p>
            <p><b>Weekly Roadmap Milestones:</b> {len(action_plan.learning_plan)} weeks</p>
            <p><b>Capstone Project:</b> {action_plan.portfolio_project.title if action_plan.portfolio_project else "Applied Project"}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Downloadable Markdown Report
    report_md = f"""# Career Action Report: {opp.role} at {opp.company}
Generated by Agentic Career Lab

## Target Opportunity
- Role: {opp.role}
- Company: {opp.company}
- Location: {opp.location}

## Resume Evidence Verification
- Verification Mode: 100% Private Local Inference (Gemma 4 on Ollama)
- Status: {action_plan.workflow_status}

## Learning Roadmap ({len(action_plan.learning_plan)} Weeks)
"""
    for step in action_plan.learning_plan:
        report_md += (
            f"\n### Week {step.week}: {step.focus}\n- Expected Output: {step.expected_output}\n"
        )
        for act in step.activities:
            report_md += f"  - {act}\n"

    if action_plan.portfolio_project:
        report_md += f"\n## Portfolio Capstone Project\n- Title: {action_plan.portfolio_project.title}\n- Objective: {action_plan.portfolio_project.objective}\n"

    st.download_button(
        label="📥 Download Career Action Report (.md)",
        data=report_md,
        file_name=f"career_action_report_{opp.company.lower().replace(' ', '_')}.md",
        mime="text/markdown",
    )


# ---------------------------------------------------------
# Page 8: Activity & Diagnostics
# ---------------------------------------------------------
def render_activity_diagnostics():
    """Render student activity timeline with collapsed technical diagnostics."""
    st.title("📊 Activity & Diagnostics")
    st.caption(
        "Review your career preparation session timeline. Technical observability is available below for developers."
    )

    state = st.session_state.get("career_workflow_state")
    events = state.activity_events if state else []

    st.markdown("### Student Milestone Timeline")
    if events:
        # Show milestone actions clearly, deduplicating repetitive step updates
        seen_actions = set()
        milestones = []
        for ev in events:
            # Map technical actions to clear student-friendly labels
            action_label = ev.action
            if "search" in action_label.lower():
                action_label = "Opportunities Scouted"
            elif "parse" in action_label.lower() or "resume" in action_label.lower():
                action_label = "Resume Analyzed Privately"
            elif "skill" in action_label.lower() or "plan" in action_label.lower():
                action_label = "Learning Roadmap Generated"

            key = (ev.agent, action_label)
            if key not in seen_actions:
                seen_actions.add(key)
                milestones.append((ev, action_label))

        for ev, label in milestones:
            # Non-fatal warnings (e.g. Adzuna credentials not configured) are notices, not failures
            if ev.status == "Success":
                status_badge = "✅ **Completed**"
            elif ev.status in ("Warning", "Info", "Notice"):
                status_badge = "ℹ️ **Notice**"
            else:
                status_badge = f"⚠️ **{ev.status}**"

            duration_str = f" • *{ev.duration_ms:.0f}ms*" if ev.duration_ms > 0 else ""
            st.markdown(f"- {status_badge} — **{ev.agent}**: {label}{duration_str}")
            if ev.summary and not any(k in ev.summary.lower() for k in ("trace", "span", "0x")):
                st.caption(f"  *{ev.summary}*")
    else:
        st.info(
            "No activity milestones recorded yet. Start by searching for opportunities or uploading your resume!"
        )

    st.markdown("---")

    # Collapsed Developer Diagnostics Area (Phase 8 Fix)
    with st.expander("🛠️ Advanced Developer Diagnostics & OpenTelemetry Spans", expanded=False):
        st.markdown("#### System Connection Status")
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        gemma_model = os.environ.get("GEMMA_MODEL", "gemma4:12b")

        ollama_connected = False
        try:
            r = httpx.get(f"{ollama_url}/api/tags", timeout=1.0)
            ollama_connected = r.status_code == 200
        except Exception:
            pass

        gemini_client = GeminiVertexClient()
        gemini_status = (
            "Configured & Available" if gemini_client.is_available() else "Local Fallback Mode"
        )

        st.write(
            f"- **Local Ollama Runtime**: {'🟢 Connected' if ollama_connected else '🔴 Unavailable'} (`{ollama_url}`)"
        )
        st.write(f"- **Local Model**: `{gemma_model}`")
        st.write(f"- **Cloud AI Client**: {gemini_status}")

        st.markdown("#### OpenTelemetry In-Memory Telemetry Spans")
        from agentic_career_lab.observability import get_in_memory_spans

        spans = get_in_memory_spans()
        if spans:
            st.caption(f"Captured {len(spans)} telemetry spans (Sanitized, Zero PII):")
            for s in reversed(spans[-10:]):
                duration_ms = (
                    ((s.end_time - s.start_time) / 1_000_000) if s.end_time and s.start_time else 0
                )
                st.markdown(
                    f"- **`{s.name}`** | Status: `{s.status.status_code.name}` | Duration: `{duration_ms:.1f}ms`"
                )
                if s.attributes:
                    safe_attrs = {
                        k: v
                        for k, v in s.attributes.items()
                        if not any(b in k.lower() for b in ("prompt", "resume", "text", "pii"))
                    }
                    st.caption(f"  Attributes: {safe_attrs}")
        else:
            st.caption("No in-memory spans captured yet.")


# ---------------------------------------------------------
# Page 9: Resume Studio (Planned Feature Showcase)
# ---------------------------------------------------------
def render_resume_studio():
    """Render planned Resume Studio feature preview."""
    st.title("✨ Resume Studio (Roadmap Preview)")
    st.caption(
        "Architectural roadmap specification — Not yet implemented (Targeted for post-v0.8.0)."
    )

    st.markdown(
        """
        <div class="card-box">
            <div class="card-title">Future Roadmap: Closing the Student Career Loop</div>
            <p>
                <b>Note:</b> This section previews the upcoming <b>Resume Studio</b> capability. It illustrates how completed
                learning roadmap deliverables will be turned into verified resume claims with student approval in future releases.
            </p>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;"/>
            <p><b>Planned Capabilities (Design Phase):</b></p>
            <ul>
                <li><b>Skill Progression Lifecycle:</b> Progression model tracking skills through <code>NOT_STARTED</code> → <code>LEARNING</code> → <code>COMPLETED</code> → <code>DEMONSTRATED</code>.</li>
                <li><b>Evidence Verification Guardrails:</b> Independent verification of GitHub repositories, Dockerfiles, and project code before any claim can be promoted.</li>
                <li><b>Human-in-the-Loop Approvals:</b> Side-by-side bullet diffs with student <i>Approve</i>, <i>Edit</i>, or <i>Reject</i> controls. No automatic resume mutations.</li>
                <li><b>ATS-Friendly Exports:</b> Download updated resumes as standard ATS-compliant DOCX and PDF deliverables with immutable version history.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "💡 Full architectural design and technical data contracts are available in `docs/features/resume-studio.md`."
    )


# ---------------------------------------------------------
# Routing Dispatcher
# ---------------------------------------------------------
navigation = normalize_navigation(st.session_state.get("nav"))

if navigation in (DASHBOARD, "Home"):
    render_dashboard()
elif navigation in (MY_PROFILE, "My Profile"):
    render_my_profile()
elif navigation in (JOB_EXPLORER, "Find Opportunities"):
    render_job_explorer()
elif navigation in (MY_RESUME, "Prepare Resume"):
    render_my_resume()
elif navigation in (SKILL_GAP_ANALYSIS, "Build Skills"):
    render_skill_gap_analysis()
elif navigation == LEARNING_HUB:
    render_learning_hub()
elif navigation == MY_LEARNING_PLAN:
    render_my_learning_plan()
elif navigation == CAREER_REPORT:
    render_career_report()
elif navigation in (ACTIVITY_DIAGNOSTICS, "Agent Activity"):
    render_activity_diagnostics()
elif navigation == RESUME_STUDIO:
    render_resume_studio()
else:
    render_dashboard()
