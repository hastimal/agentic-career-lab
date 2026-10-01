"""Streamlit UI Shell for Agentic Career Lab."""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Agentic Career Lab",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# Session State for Defaults
if "preset_prompt" not in st.session_state:
    st.session_state["preset_prompt"] = ""
if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""

# Sidebar Navigation & Settings
with st.sidebar:
    st.title("🎓 Agentic Career Lab")
    st.caption("Privacy-Aware Hybrid Multi-Agent Platform")

    st.markdown("---")
    navigation = st.radio(
        "Navigation",
        [
            "Overview",
            "Chat",
            "Opportunities",
            "Private Resume",
            "Skill Builder",
            "Agent Activity",
        ],
        index=0,
    )

    st.markdown("---")
    with st.expander("📝 Demo Student Profile", expanded=False):
        st.text_input("Major", value="Computer Science")
        st.text_input("Graduation Year", value="2027")
        st.text_input("Location", value="Texas")
        st.text_input("Preferred Role", value="AI Engineering Intern")
        st.text_area("Skills", value="Python, SQL, Docker, Google Cloud, REST APIs")
        st.caption("These are editable demo defaults.")

    st.markdown("---")
    st.subheader("Planned Architecture")
    st.markdown(
        """
        <div style="font-size: 0.85rem; line-height: 1.8;">
        <div><b>Cloud Runtime:</b>
            <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
        </div>
        <div style="margin-top: 6px;"><b>Local Runtime:</b>
            <span class="model-badge-local">🔒 Gemma 4 Local / Ollama</span>
        </div>
        <div style="margin-top: 6px;"><b>Deterministic:</b>
            <span class="model-badge-python">⚙ Python</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview():
    """Render landing screen."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Agentic Career Lab</div>
            <div class="hero-subtitle">
                Find the opportunity.<br>
                Understand your gaps.<br>
                Build the skills.<br>
                Apply with confidence.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="badge-container">
            <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
            <span class="model-badge-local">🔒 Gemma 4 Local / Ollama</span>
            <span class="model-badge-python">⚙ Deterministic Python</span>
        </div>
        <p style="color: gray; font-size: 0.9em;"><em>Note: These are planned/future capabilities in Milestone 1.</em></p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Find Internships", key="btn_opps", use_container_width=True):
            st.session_state["nav"] = "Opportunities"
            st.rerun()

    with col2:
        if st.button("Analyze Resume", key="btn_resume", use_container_width=True):
            st.session_state["nav"] = "Private Resume"
            st.rerun()

    with col3:
        if st.button("Build My Skills", key="btn_skills", use_container_width=True):
            st.session_state["nav"] = "Skill Builder"
            st.rerun()

    with col4:
        if st.button("Full Career Workflow", key="btn_workflow", use_container_width=True):
            st.session_state["nav"] = "Chat"
            st.rerun()


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
            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": "*(Demo Shell)* Coordinator received your message. In upcoming milestones, this orchestrates Job Scout, Resume Agent, and Skill Builder.",
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

    st.info("Evidence-backed Job Scout arrives in Milestone 2.")

    with st.expander("Demo Search Form", expanded=True):
        st.text_input("Role", value="AI Engineering Intern")
        st.text_input("Location", value="Texas")
        st.selectbox("Internship only", ["Yes", "No"], index=0)
        st.text_area("Skills", value="Python, SQL, Docker, Google Cloud, REST APIs")
        if st.button("Find Opportunities"):
            st.toast("Job Scout arrives in Milestone 2")

    st.markdown("### DEMO DATA")
    st.markdown(
        """
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h3 style="margin: 0; color: #0f172a;">AI / ML Engineering Intern</h3>
                    <p style="margin: 4px 0; color: #64748b;">
                        Google Cloud • Sunnyvale, CA (Hybrid)
                    </p>
                </div>
            </div>
            <div style="margin-top: 12px; background: #f8fafc; padding: 12px; border-radius: 8px;">
                <div style="color: #15803d; font-weight: 600;">✓ Strong Evidence:</div>
                <div style="color: #334155; font-size: 0.9rem; margin-bottom: 8px;">Python, SQL, Docker</div>
                <div style="color: #b45309; font-weight: 600;">△ Missing Evidence:</div>
                <div style="color: #334155; font-size: 0.9rem;">Vertex AI, Kubernetes</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_private_resume():
    """Render Private Resume Lab."""
    st.title("🔒 Private Resume Lab")
    st.caption("Gemma 4 via local Ollama")

    st.info(
        "Resume analysis is designed to run locally so raw resume content does not need to be sent to a cloud model."
    )

    demo_resume = "Alex Student\nB.S. Computer Science, Expected 2027\n\nSkills:\nPython, SQL, Docker, Google Cloud, REST APIs\n\nProject:\nBuilt a Python REST API and containerized it with Docker.\n\nExperience:\nStudent Developer — Example University Lab\nBuilt internal Python utilities and worked with SQL datasets."

    if st.button("Load Demo Resume"):
        st.session_state["resume_text"] = demo_resume
        st.rerun()

    resume_input = st.text_area(
        "Paste Resume Markdown / Text",
        height=200,
        value=st.session_state["resume_text"],
        placeholder=(
            "Education: B.S. Computer Science...\\n"
            "Projects: Built high-throughput API with Python and Docker..."
        ),
    )

    if resume_input == demo_resume:
        st.caption("SYNTHETIC DEMO RESUME")

    if st.button("Analyze Resume Privately", type="primary"):
        st.warning("Gemma 4 integration arrives in Milestone 3. Do not run Gemma yet.")


def render_skill_builder():
    """Render Skill Builder UI."""
    st.title("🛠️ Skill Builder Agent")
    st.caption("DEMO PREVIEW — live Skill Builder arrives in Milestone 4.")

    st.subheader("Target Role: AI Engineering Intern")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Demonstrated")
        st.success("✓ Python\n\n✓ SQL\n\n✓ Docker")

    with c2:
        st.markdown("#### Example Gaps")
        st.warning("△ Vertex AI\n\n△ Google ADK\n\n△ Kubernetes")

    st.markdown("---")
    st.subheader("Example 4-Week Plan")
    st.markdown(
        """
        - **Week 1** — Gemini + Vertex AI fundamentals
        - **Week 2** — Google ADK + tool calling
        - **Week 3** — Build an agentic AI project
        - **Week 4** — Docker + Cloud Run + documentation
        """
    )


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

    if st.button("Replay Demo Trace", disabled=True):
        pass


# Handle navigation from state if changed via button
if "nav" in st.session_state:
    navigation = st.session_state["nav"]
    del st.session_state["nav"]

# Routing logic
if navigation == "Overview":
    render_overview()
elif navigation == "Chat":
    render_chat()
elif navigation == "Opportunities":
    render_opportunities()
elif navigation == "Private Resume":
    render_private_resume()
elif navigation == "Skill Builder":
    render_skill_builder()
elif navigation == "Agent Activity":
    render_agent_activity()
