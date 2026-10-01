"""Streamlit UI Shell for Agentic Career Lab."""

import streamlit as st

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.agents.resume_agent.agent import PrivateResumeAgent
from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.agents.skill_builder.planner import FakePlanningLLM
from agentic_career_lab.coordinator import (
    ADKCareerCoordinator,
    CareerAction,
    CareerCoordinator,
    CareerWorkflowState,
    LocalResumeContext,
)
from agentic_career_lab.llm.local import FakeGemmaClient
from agentic_career_lab.models import OpportunitySearchQuery, StudentProfile
from agentic_career_lab.providers.adzuna import (
    AdzunaOpportunityProvider,
)
from agentic_career_lab.providers.mock import MockOpportunityProvider
from agentic_career_lab.services.resume_parser import ResumeParser
from agentic_career_lab.ui_helpers import (
    ACTIVITY,
    HOME,
    OPPORTUNITIES,
    RESUME,
    SKILLS,
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
    st.session_state["nav"] = page
    st.rerun()


# Custom Styling for modern AI Career Workspace
st.markdown(
    """
    <style>
    /* Metric & Model Badges */
    .badge-container {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        align-items: center;
    }
    .model-badge-cloud {
        background-color: #E8F0FE;
        color: #1A73E8;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #D2E3FC;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .model-badge-local {
        background-color: #E6F4EA;
        color: #137333;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #CEEAD6;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .model-badge-python {
        background-color: #f3f4f6;
        color: #374151;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #e5e7eb;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .hero-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #334155;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state() -> None:
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
        "nav": "Home",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "coordinator" not in st.session_state:
        domain_coord = CareerCoordinator(
            job_scout=JobScoutAgent(provider=MockOpportunityProvider()),
            resume_agent=PrivateResumeAgent(llm=FakeGemmaClient(is_online=True)),
            skill_builder=SkillBuilderAgent(llm=FakePlanningLLM()),
        )
        st.session_state["coordinator"] = ADKCareerCoordinator(domain_coord)
    if "career_workflow_state" not in st.session_state:
        st.session_state["career_workflow_state"] = CareerWorkflowState()


initialize_session_state()

# Sidebar Navigation & Settings
with st.sidebar:
    st.title("🎓 Agentic Career Lab")
    st.caption("Privacy-Aware Hybrid Multi-Agent Platform")

    st.markdown("---")

    st.markdown("### Navigation")
    if st.button("Home", use_container_width=True):
        navigate(HOME)
    if st.button("Find Opportunities", use_container_width=True):
        navigate(OPPORTUNITIES)
    if st.button("Prepare Resume", use_container_width=True):
        navigate(RESUME)
    if st.button("Build Skills", use_container_width=True):
        navigate(SKILLS)

    st.markdown("### Advanced")
    if st.button("Agent Activity", use_container_width=True):
        navigate(ACTIVITY)

    st.markdown("---")
    with st.expander("📝 Demo Student Profile", expanded=False):
        st.text_input("Major", value="Computer Science")
        st.text_input("Graduation Year", value="2027")
        st.text_input("Location", value="Texas")
        st.text_input("Preferred Role", value="AI Engineering Intern")
        st.text_area("Skills", value="Python, SQL, Docker, Google Cloud, REST APIs")
        st.caption("These are editable demo defaults.")

    st.markdown("---")
    with st.expander("Technical Architecture"):
        st.markdown(
            """
            <div style="font-size: 0.85rem; line-height: 1.8;">
            <div><b>Cloud AI:</b>
                <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
            </div>
            <div style="margin-top: 6px;"><b>Private Local AI:</b>
                <span class="model-badge-local">🔒 Gemma 4 Local / Ollama</span>
            </div>
            <div style="margin-top: 6px;"><b>Deterministic Logic:</b>
                <span class="model-badge-python">⚙ Python</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_home():
    """Render landing screen."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Agentic Career Lab</div>
            <div class="hero-subtitle">
                Find the opportunity.<br>
                Prepare your resume.<br>
                Build the missing skills.<br>
            </div>
            <p>A privacy-aware career preparation assistant for students.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Progress tracking
    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")
    plan = st.session_state.get("skill_builder_plan")

    progress = get_workflow_progress(opp, analysis, plan)

    st.markdown("### Career Preparation Progress")
    if progress["opportunity_selected"]:
        st.success("✓ Opportunity selected")
    else:
        st.info("○ Select an opportunity")

    if progress["resume_analyzed"]:
        st.success("✓ Resume analyzed")
    else:
        st.info("○ Analyze your resume")

    if progress["skill_plan_built"]:
        st.success("✓ Skill plan built")
    else:
        st.info("○ Build your skill plan")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### STEP 1: Find Opportunity")
        st.write("Discover internships and understand what each role requires.")
        if st.button("Find Opportunities", key="btn_step1"):
            navigate(OPPORTUNITIES)

        st.markdown("---")
        st.markdown("### STEP 2: Prepare Resume")
        st.write("Upload your resume and compare it privately against the selected role.")
        st.markdown("🔒 Local Resume Analysis")
        if st.button("Prepare Resume", key="btn_step2"):
            navigate(RESUME)

        st.markdown("---")
        st.markdown("### STEP 3: Build Skills")
        st.write("Identify skill gaps and get a practical learning plan with trusted resources.")
        if st.button("Build Skills", key="btn_step3"):
            navigate(SKILLS)

    with col2:
        st.markdown("### Current Target")
        if opp:
            st.info(f"**{opp.role}**\\n\\n{opp.company}\\n\\n{opp.location}")
            if analysis:
                st.write("**Status:** Resume analyzed")
                st.write("**Next step:** Build your skill plan")
                if st.button("Continue", key="btn_cont_skills"):
                    navigate(SKILLS)
            else:
                st.write("**Status:** Opportunity selected")
                st.write("**Next step:** Prepare your resume")
                if st.button("Continue", key="btn_cont_resume"):
                    navigate(RESUME)
        else:
            st.info("No opportunity selected yet.")
            if st.button("Find Opportunity", key="btn_cont_opps"):
                navigate(OPPORTUNITIES)


def render_chat():
    """Render multi-agent chat interface."""
    st.title("💬 Career Coordinator Chat")
    st.caption("Coordinate your career planning with Google ADK multi-agent orchestration")

    st.info("Live agent execution begins in later milestones.")

    st.markdown("**Preset Prompts:**")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("AI / Cloud Internship", use_container_width=True):
        st.session_state["preset_prompt"] = (
            "I'm a junior computer science student. I know Python, SQL, Docker, and basic Google Cloud. Find AI/cloud internships, compare my skills, and tell me what I should learn next."
        )
        st.rerun()
    if c2.button("Private Resume Review", use_container_width=True):
        st.session_state["preset_prompt"] = (
            "Compare my resume against the selected AI Engineering Intern role. Improve wording using only evidence already present in my resume. Do not invent skills, metrics, or accomplishments."
        )
        st.rerun()
    if c3.button("Skill Builder", use_container_width=True):
        st.session_state["preset_prompt"] = (
            "Based on the selected internship and my current evidence, identify my top three skill gaps and create a 4-week learning plan with one portfolio project."
        )
        st.rerun()
    if c4.button("Full Agentic Flow", use_container_width=True):
        st.session_state["preset_prompt"] = (
            "Find an AI/cloud internship that fits my profile, analyze my resume privately, identify missing skills, and create a preparation plan."
        )
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your Career Coordinator. I can help discover internships, "
                    "privately evaluate your resume on your machine with Gemma 4, "
                    "or build a personalized skill acquisition plan. How can I help you today?"
                ),
            }
        ]

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    with st.form("chat_form", clear_on_submit=True):
        prompt = st.text_area(
            "Ask about internships, resume feedback, or skill roadmaps...",
            value=st.session_state["preset_prompt"],
            height=100,
        )
        submitted = st.form_submit_button("Send")
        if submitted and prompt:
            st.session_state["preset_prompt"] = ""
            st.session_state["messages"].append({"role": "user", "content": prompt})

            # Simple integration for Job Scout
            if "internship" in prompt.lower() or "find" in prompt.lower():
                profile = StudentProfile(
                    name="Student",
                    target_role="AI Engineering Intern",
                    education_level="Junior",
                    major="Computer Science",
                    skills=["Python", "SQL", "Docker", "Google Cloud", "REST APIs"],
                )
                query = OpportunitySearchQuery(
                    role="Intern", location="Texas", internship_only=True, keywords=[]
                )
                matches = st.session_state["job_scout_agent"].run(profile, query)
                st.session_state["agent_events"] = st.session_state["job_scout_agent"].events
                st.session_state["job_matches"] = matches

                msg = "Job Scout prepared search, loaded opportunities, extracted requirements, and compared skills. Check Opportunities and Agent Activity."
            else:
                msg = "*(Demo Shell)* Coordinator received your message. In upcoming milestones, this orchestrates Job Scout, Resume Agent, and Skill Builder."

            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": msg,
                }
            )
            st.rerun()

    st.markdown("---")
    st.markdown("### Workflow Preview")
    st.code(
        "Career Coordinator\n→ Job Scout\n→ Private Resume Agent\n→ Skill Builder", language="text"
    )


def render_opportunities():
    """Render Opportunities UI."""
    st.title("🎯 Job Scout — Opportunities")
    st.caption("Evidence-backed opportunity matching with verified source URLs")

    with st.expander("Search Form", expanded=True):
        role = st.text_input("Role", value="AI Engineering Intern")
        location = st.text_input("Location", value="Texas")
        internship_only = st.selectbox("Internship only", ["Yes", "No"], index=0)
        skills = st.text_area("Skills", value="Python, SQL, Docker, Google Cloud, REST APIs")
        source = st.radio("Source:", ["Live Jobs", "Demo Data"], index=1, horizontal=True)

        if st.button("Find Opportunities"):
            if source == "Live Jobs":
                try:
                    provider = AdzunaOpportunityProvider()
                except Exception as e:
                    st.error(str(e))
                    st.stop()
            else:
                provider = MockOpportunityProvider()

            # Inject provider
            st.session_state["coordinator"].domain_coordinator.job_scout.provider = provider
            st.session_state["job_source_label"] = "LIVE" if source == "Live Jobs" else "DEMO DATA"

            profile = StudentProfile(
                name="Student",
                target_role=role,
                education_level="Junior",
                major="Computer Science",
                skills=[s.strip() for s in skills.split(",") if s.strip()],
            )
            query = OpportunitySearchQuery(
                role=role,
                location=location,
                internship_only=(internship_only == "Yes"),
                keywords=[],
            )
            state = st.session_state["career_workflow_state"]
            state.student_profile = profile
            state.search_query = query

            # Delegate to Coordinator
            st.session_state["coordinator"].execute_action(CareerAction.FIND_OPPORTUNITIES, state)

            # Sync back to session state for existing UI components
            st.session_state["job_matches"] = state.opportunities
            st.session_state["agent_events"] = state.activity_events

    label = st.session_state.get("job_source_label", "DEMO DATA")
    st.markdown(f"### {label}")

    if not st.session_state["job_matches"]:
        st.info("No matches found. Run a search to see mock opportunities.")

    for match in st.session_state["job_matches"]:
        opp = match.opportunity
        st.markdown(
            f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; color: #0f172a;">
                            {opp.role} <span style="font-size: 0.7em; background: {"#dbeafe" if not getattr(opp, "is_demo", True) else "#f3f4f6"}; color: {"#1e40af" if not getattr(opp, "is_demo", True) else "#4b5563"}; padding: 2px 6px; border-radius: 4px; margin-left: 8px; vertical-align: middle;">{"LIVE" if not getattr(opp, "is_demo", True) else "DEMO DATA"}</span>
                        </h3>
                        <p style="margin: 4px 0; color: #64748b;">
                            {opp.company} • {opp.location}
                        </p>
                    </div>
                </div>
                <div style="margin-top: 12px; background: #f8fafc; padding: 12px; border-radius: 8px;">
                    <div style="color: #15803d; font-weight: 600;">✓ Demonstrated:</div>
                    <div style="color: #334155; font-size: 0.9rem; margin-bottom: 8px;">{", ".join(match.demonstrated_skills) if match.demonstrated_skills else "None"}</div>
                    <div style="color: #b45309; font-weight: 600;">△ Partial:</div>
                    <div style="color: #334155; font-size: 0.9rem; margin-bottom: 8px;">{", ".join(match.partial_skills) if match.partial_skills else "None"}</div>
                    <div style="color: #ef4444; font-weight: 600;">✗ Missing:</div>
                    <div style="color: #334155; font-size: 0.9rem; margin-bottom: 8px;">{", ".join(match.missing_skills) if match.missing_skills else "None"}</div>
                </div>
                <div style="margin-top: 12px;">
                    <p><b>Why relevant:</b> {match.why_relevant}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("View Source", opp.source_url)
        with c2:
            if st.button("Prepare My Resume", key=f"prep_btn_{opp.opportunity_id}"):
                st.session_state["selected_opportunity"] = opp
                navigate(RESUME)


def render_private_resume():
    """Render Private Resume Lab."""
    st.title("🔒 Private Resume Lab")
    st.caption("Gemma 4 via local Ollama")

    st.info("Resume analysis runs locally. Raw resume content is not sent to Gemini or Vertex AI.")

    selected_opp = st.session_state.get("selected_opportunity")
    if selected_opp:
        st.write(f"**Target Role:** {selected_opp.role} at {selected_opp.company}")
    else:
        st.info("No target opportunity is selected yet.")
        st.write(
            "You can analyze your resume privately now, or select an opportunity first for role-specific evidence matching."
        )
        if st.button("Find an Opportunity"):
            navigate(OPPORTUNITIES)

    st.markdown("---")
    st.write("### Choose how to provide your resume:")

    tab_upload, tab_paste, tab_demo = st.tabs(["Upload Resume", "Paste Resume Text", "Load Demo"])

    with tab_upload:
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("File is too large. Max size is 5MB.")
            else:
                parser = ResumeParser()
                parsed = parser.parse_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)

                if parsed.extraction_warnings:
                    for warning in parsed.extraction_warnings:
                        st.warning(warning)

                if parsed.text.strip():
                    st.session_state["resume_text"] = parsed.text
                    st.session_state["resume_source"] = "upload"
                    st.session_state["resume_file_name"] = parsed.file_name
                    st.success("✓ Resume loaded locally")
                    st.caption(f"File: {parsed.file_name}")
                    st.caption("Privacy: 🔒 Processed locally")

    with tab_paste:
        resume_input = st.text_area(
            "Paste Resume Markdown / Text",
            height=200,
            value=st.session_state["resume_text"]
            if st.session_state["resume_source"] == "paste"
            else "",
            placeholder=(
                "Education: B.S. Computer Science...\\n"
                "Projects: Built high-throughput API with Python and Docker..."
            ),
        )
        if resume_input:
            st.session_state["resume_text"] = resume_input
            st.session_state["resume_source"] = "paste"
            st.session_state["resume_file_name"] = ""

    with tab_demo:
        demo_resume = "Alex Student\\nB.S. Computer Science, Expected 2027\\n\\nSkills:\\nPython, SQL, Docker, Google Cloud, REST APIs\\n\\nProject:\\nBuilt a Python REST API and containerized it with Docker.\\n\\nExperience:\\nStudent Developer — Example University Lab\\nBuilt internal Python utilities and worked with SQL datasets."
        if st.button("Load Demo Resume"):
            st.session_state["resume_text"] = demo_resume
            st.session_state["resume_source"] = "paste"
            st.session_state["resume_file_name"] = "demo_resume"
            st.rerun()

    st.markdown("---")

    if st.button("Analyze Resume Privately", type="primary"):
        resume_content = st.session_state.get("resume_text", "").strip()
        if not resume_content:
            st.error("Please provide resume text either by pasting or uploading.")
            return

        try:
            state = st.session_state["career_workflow_state"]
            local_context = LocalResumeContext(raw_resume_text=resume_content)

            st.session_state["coordinator"].execute_action(
                CareerAction.PREPARE_RESUME, state, local_resume=local_context
            )

            st.session_state["resume_analysis"] = state.resume_analysis
            st.session_state["agent_events"] = state.activity_events

        except Exception as e:
            st.error(
                f"Private resume analysis is unavailable because the local Ollama runtime is not running. Or another error occurred: {str(e)}"
            )

    if "resume_analysis" in st.session_state:
        analysis = st.session_state["resume_analysis"]
        st.subheader("A. Extracted Resume Evidence")
        st.write("**Skills:**")
        st.write(
            "- "
            + "\\n- ".join(
                analysis.suggestions[0].evidence_used
                if analysis.suggestions
                else ["Python", "SQL", "Docker", "Google Cloud", "REST APIs"]
            )
        )

        st.subheader("B. Job Requirement Mapping")
        if not analysis.requirement_matches:
            st.write("No opportunity selected.")
        for match in analysis.requirement_matches:
            status_icon = (
                "✓" if match.status == "Demonstrated" else "△" if match.status == "Partial" else "✗"
            )
            color = (
                "#15803d"
                if match.status == "Demonstrated"
                else "#b45309"
                if match.status == "Partial"
                else "#ef4444"
            )
            st.markdown(
                f"<div style='color: {color}; font-weight: 600;'>{status_icon} {match.requirement}</div>",
                unsafe_allow_html=True,
            )
            if match.evidence:
                st.caption(f"Evidence: {match.evidence}")

        st.subheader("C. Resume Suggestions")
        for sugg in analysis.suggestions:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**CURRENT**")
                st.info(sugg.original_text)
            with c2:
                st.markdown("**SUGGESTED**")
                st.success(sugg.suggested_text)

            st.caption(f"Evidence used: {', '.join(sugg.evidence_used)}")
            if sugg.accepted:
                st.markdown(
                    "<div style='color: #15803d;'>Safety: ✓ No unsupported claims</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='color: #ef4444;'>⚠ Unsupported claim detected</div>",
                    unsafe_allow_html=True,
                )
                st.write(sugg.unsupported_claims_detected)

        if st.button("Build My Skill Plan", type="primary"):
            navigate(SKILLS)


def render_skill_builder():
    """Render Skill Builder UI."""
    st.title("🛠️ Build Missing Skills")
    st.caption(
        "Turn the gaps between your resume and your selected opportunity into a practical learning plan."
    )

    opp = st.session_state.get("selected_opportunity")
    analysis = st.session_state.get("resume_analysis")

    if not opp:
        st.info("Start by selecting an opportunity from the Opportunities page.")
        return

    if not analysis:
        st.info("Analyze your resume first so the Skill Builder can identify evidence-based gaps.")
        if st.button("Go to Private Resume Lab"):
            navigate(RESUME)
        return

    st.markdown(f"**Target Role:** {opp.role} at {opp.company}")

    duration = st.radio("Plan Duration", ["2 Weeks", "4 Weeks"], index=1, horizontal=True)
    weeks = 2 if duration == "2 Weeks" else 4
    _ = weeks

    if st.button("Build My Learning Plan", type="primary"):
        state = st.session_state["career_workflow_state"]

        st.session_state["coordinator"].execute_action(CareerAction.BUILD_SKILLS, state)

        st.session_state["skill_builder_plan"] = state.skill_builder_plan
        st.session_state["agent_events"] = state.activity_events

    if "skill_builder_plan" in st.session_state:
        plan = st.session_state["skill_builder_plan"]

        st.markdown("### B. What You Already Demonstrate")
        for s in plan.strengths:
            st.success(f"✓ {s}")

        st.markdown("### C. Priority Skill Gaps")
        for gap in plan.priority_gaps:
            if gap.status in ("Missing", "Partial"):
                color = "#b45309" if gap.status == "Partial" else "#ef4444"
                st.markdown(
                    f"**<span style='color: {color};'>{gap.priority.upper()}</span> {gap.skill}**",
                    unsafe_allow_html=True,
                )
                st.caption(f"Why: {gap.reason}")

        st.markdown(f"### D. {duration} Learning Plan")
        for step in plan.learning_steps:
            with st.expander(f"Week {step.week}: {step.focus}", expanded=True):
                st.write("**Activities:**")
                for act in step.activities:
                    st.write(f"- {act}")
                st.write(f"**Expected Output:** {step.expected_output}")

        st.markdown("### E. Recommended Learning Resources")
        for res in plan.recommended_resources:
            st.markdown(f"#### {res.skill}")
            st.markdown(f"**{res.resource_type.upper()}**")
            st.write(res.title)
            st.caption(f"Type: {res.resource_type}\\n\\nWhy: {res.reason}")
            if res.url:
                st.link_button("Open Resource", res.url)
            else:
                st.info(f"Recommended search: {res.skill} beginner tutorial")
            st.markdown("---")

        if plan.portfolio_project:
            st.markdown("### F. Suggested Portfolio Project")
            st.info(f"**{plan.portfolio_project.title}**\\n\\n{plan.portfolio_project.objective}")
            st.write("**Skills practiced:** " + ", ".join(plan.portfolio_project.skills_practiced))
            st.write("**Deliverables:** " + ", ".join(plan.portfolio_project.deliverables))


def render_agent_activity():
    """Render Agent Activity / Telemetry View."""
    st.title("📊 Agent Activity & Execution Flow")
    st.caption("Preview only — live agent execution starts in later milestones.")

    st.markdown("### Future Runtime Routing")
    st.markdown(
        """
        <div class="badge-container">
            <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
            <span style="font-size: 0.9em; color: gray;">Current information + reasoning</span>
        </div>
        <div class="badge-container">
            <span class="model-badge-local">🔒 Gemma 4 / Ollama</span>
            <span style="font-size: 0.9em; color: gray;">Private resume analysis</span>
        </div>
        <div class="badge-container">
            <span class="model-badge-python">⚙ Python</span>
            <span style="font-size: 0.9em; color: gray;">Deterministic matching + validation</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Full Future Flow")
    st.code(
        """
Career Coordinator
   ↓
Job Scout
   ├── parse_goal()
   ├── search_opportunities()
   ├── normalize_results()
   └── extract_requirements()
   ↓
Private Resume Agent
   ├── connect_ollama()
   ├── analyze_resume()
   ├── map_evidence()
   └── validate_claims()
   ↓
Skill Builder
   ├── compare_requirements()
   ├── prioritize_gaps()
   └── create_learning_plan()
   ↓
Final Career Action Plan
        """,
        language="text",
    )

    st.markdown("### Example Future Status")
    st.markdown(
        """
        - ○ Coordinator      not running
        - ○ Job Scout        not running
        - ○ Resume Agent     not running
        - ○ Skill Builder    not running
        """
    )

    if st.session_state["agent_events"]:
        st.markdown("### Agent Execution Events")
        for event in st.session_state["agent_events"]:
            # Check if event is dict (from old logic) or Pydantic model (new logic)
            if isinstance(event, dict):
                st.text(
                    f"{event.get('status', 'Unknown')} {event.get('step', 'unknown_step'):<25} {event.get('duration', 0)}s"
                )
            else:
                st.markdown(
                    f"**{event.agent}** | {event.status} | {event.runtime} | {event.duration_ms}ms"
                )
                st.text(f"→ {event.action}: {event.summary}")

    if st.button("Replay Demo Trace", disabled=True):
        pass


# Handle navigation from state if changed via button
navigation = normalize_navigation(st.session_state.get("nav"))

# Routing logic
if navigation == HOME:
    render_home()
elif navigation == OPPORTUNITIES:
    render_opportunities()
elif navigation == RESUME:
    render_private_resume()
elif navigation == SKILLS:
    render_skill_builder()
elif navigation == ACTIVITY:
    render_agent_activity()
else:
    # Safe fallback
    navigate(HOME)
