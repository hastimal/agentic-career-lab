"""Streamlit UI Shell for OpenCareer Agents."""

import streamlit as st

from opencareer_agents.config import settings

# Page configuration
st.set_page_config(
    page_title="OpenCareer Agents",
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
    .privacy-tag {
        display: flex;
        gap: 20px;
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-top: 1.5rem;
        border-top: 1px solid #334155;
        padding-top: 1.2rem;
    }
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
    }
    .dark-card {
        background: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation & Settings
with st.sidebar:
    st.title("🎓 OpenCareer Agents")
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
    st.subheader("System Status")
    st.markdown(
        f"""
        <div style="font-size: 0.85rem; line-height: 1.8;">
        <div><b>Cloud Runtime:</b>
            <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
        </div>
        <div style="margin-top: 6px;"><b>Local Runtime:</b>
            <span class="model-badge-local">🔒 Gemma Local ({settings.gemma_model})</span>
        </div>
        <div style="margin-top: 6px; color: gray;">Ollama: {settings.ollama_base_url}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview():
    """Render landing screen."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">OpenCareer Agents</div>
            <div class="hero-subtitle">
                Find the opportunity.<br>
                Understand your gaps.<br>
                Build the skills.<br>
                Apply with confidence.
            </div>
            <div class="privacy-tag">
                <span>🔒 <b>Private resume analysis with Gemma</b></span>
                <span>☁ <b>Current opportunity intelligence with Gemini</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔍 Find Internships")
        st.write(
            "Evidence-backed opportunity scouting powered by Gemini and verifiable job sources."
        )
        if st.button("Explore Opportunities", key="btn_opps", use_container_width=True):
            st.session_state["nav"] = "Opportunities"
            st.rerun()

    with col2:
        st.markdown("### 🔒 Analyze Resume")
        st.write("Local, zero-cloud data leak resume analysis and bullet refinement using Gemma 4.")
        if st.button("Open Resume Lab", key="btn_resume", use_container_width=True):
            st.session_state["nav"] = "Private Resume"
            st.rerun()

    with col3:
        st.markdown("### 🛠️ Build My Skills")
        st.write(
            "Deterministic gap analysis with personalized 4-week roadmaps and portfolio ideas."
        )
        if st.button("Start Skill Builder", key="btn_skills", use_container_width=True):
            st.session_state["nav"] = "Skill Builder"
            st.rerun()

    st.markdown("---")
    st.subheader("Active Agent Architecture")
    st.code(
        """
Student
   ↓
Career Coordinator — Google ADK
   │
   ├── Job Scout Agent ─────────────── ☁ Gemini / Vertex AI (Opportunity Discovery)
   │
   ├── Private Resume Agent ────────── 🔒 Gemma 4 via Local Ollama (Local Privacy Boundary)
   │
   └── Skill Builder Agent ─────────── ⚙ Deterministic Python + ☁ Gemini Reasoning
        """,
        language="text",
    )


def render_chat():
    """Render multi-agent chat interface."""
    st.title("💬 Career Coordinator Chat")
    st.caption("Coordinate your career planning with Google ADK multi-agent orchestration")

    st.markdown(
        """
        <div class="badge-container">
            <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
            <span class="model-badge-local">🔒 Gemma Local</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    if prompt := st.chat_input("Ask about internships, resume feedback, or skill roadmaps..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            response = (
                f"*(Demo Shell)* Coordinator received: '{prompt}'. In upcoming milestones, "
                "this orchestrates Job Scout, Resume Agent, and Skill Builder."
            )
            st.write(response)
            st.session_state["messages"].append({"role": "assistant", "content": response})


def render_opportunities():
    """Render Opportunities UI."""
    st.title("🎯 Job Scout — Opportunities")
    st.caption("Evidence-backed opportunity matching with verified source URLs")

    st.markdown(
        """
        <div class="badge-container">
            <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.text_input(
        "Search roles or keywords",
        value="AI Engineering Intern",
        placeholder="e.g. Cloud Engineer Intern, Python Developer",
    )

    # Demo opportunity card
    st.markdown("### Current Opportunities")
    with st.container():
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
                    <span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px;
                        border-radius: 8px; font-size: 0.8rem; font-weight: 600;">
                        Verified Source
                    </span>
                </div>
                <div style="margin-top: 12px; font-size: 0.95rem;">
                    <b>Source:</b>
                    <a href="https://careers.google.com" target="_blank">
                        Google Careers Listing #84920
                    </a>
                </div>
                <div style="margin-top: 12px; background: #f8fafc; padding: 12px;
                    border-radius: 8px;">
                    <div style="color: #15803d; font-weight: 600;">✓ Strong Evidence:</div>
                    <div style="color: #334155; font-size: 0.9rem; margin-bottom: 8px;">
                        Python, Git, Docker, REST APIs
                    </div>
                    <div style="color: #b45309; font-weight: 600;">△ Missing Evidence:</div>
                    <div style="color: #334155; font-size: 0.9rem;">
                        Vertex AI, Google ADK, Kubernetes
                    </div>
                </div>
                <div style="margin-top: 12px; font-size: 0.9rem; color: #475569;">
                    <b>Why Relevant:</b> Matches your junior CS coursework in distributed systems
                    and hands-on Python backend projects.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([1, 4])
        with c1:
            st.button("Prepare Me", key="prep_1")
        with c2:
            st.link_button("View Role", "https://careers.google.com", key="link_1")


def render_private_resume():
    """Render Private Resume Lab."""
    st.title("🔒 Private Resume Lab")
    st.caption("100% Local Resume Analysis powered by Gemma 4 via Ollama")

    st.markdown(
        """
        <div class="badge-container">
            <span class="model-badge-local">🔒 Gemma Local (gemma4:12b)</span>
        </div>
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0;
            color: #166534; padding: 12px; border-radius: 8px; margin-bottom: 20px;">
            🛡️ <b>Privacy Guarantee:</b> Your resume content never leaves this machine.
            It is processed strictly via your local Ollama daemon.
        </div>
        """,
        unsafe_allow_html=True,
    )

    resume_input = st.text_area(
        "Paste Resume Markdown / Text",
        height=200,
        placeholder=(
            "Education: B.S. Computer Science...\n"
            "Projects: Built high-throughput API with Python and Docker..."
        ),
    )

    if st.button("Analyze Resume Privately", type="primary"):
        if resume_input:
            st.success("Resume parsed locally via Gemma (Demo Shell)")
        else:
            st.warning("Please paste resume text to test.")

    st.markdown("### Job Requirement → Resume Evidence (Demo)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            - **Python** `✓ Backend project`
            - **Docker** `✓ Deployment project`
            - **Vertex AI** `— No evidence found`
            """
        )
    with col2:
        st.markdown(
            """
            - **Git & GitHub** `✓ Open source contributions`
            - **Google ADK** `— No evidence found`
            """
        )


def render_skill_builder():
    """Render Skill Builder UI."""
    st.title("🛠️ Skill Builder Agent")
    st.caption("Deterministic gap analysis & personalized 4-week learning plans")

    st.markdown(
        """
        <div class="badge-container">
            <span class="model-badge-cloud">☁ Gemini / Vertex AI</span>
            <span class="model-badge-local">⚙ Deterministic Python</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Target: AI Engineering Intern")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Demonstrated Strengths")
        st.success("✓ Python (Advanced)\n\n✓ SQL & Relational Databases\n\n✓ Docker Containers")

    with c2:
        st.markdown("#### Priority Gaps")
        st.warning(
            "△ Google Cloud Vertex AI (Required)\n\n"
            "△ Google ADK Multi-Agent (Required)\n\n"
            "△ Kubernetes (Preferred)"
        )

    st.markdown("---")
    st.subheader("Recommended 4-Week Action Plan")
    st.markdown(
        """
        - **Week 1: Vertex AI Fundamentals** — Hands-on Gemini API integration and model evaluation.
        - **Week 2: Multi-Agent Architectures with ADK** — Build a coordinator and tool agents.
        - **Week 3: Local-Cloud Hybrid Patterns** — Connect local Gemma inference to orchestrators.
        - **Week 4: Portfolio Project** — Deploy a live multi-agent career advisor on Cloud Run.
        """
    )


def render_agent_activity():
    """Render Agent Activity / Telemetry View."""
    st.title("📊 Agent Activity & Observability")
    st.caption("Trace multi-agent execution events, model routing, and latency")

    st.markdown(
        """
        <div class="badge-container">
            <span class="model-badge-cloud">☁ Gemini</span>
            <span class="model-badge-local">🔒 Gemma 4 Local</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Execution Pipeline")
    st.code(
        """
Career Coordinator
   ↓
Job Scout
   ├─ search_opportunities (Google Careers)
   └─ extract_requirements (Gemini 1.5 Flash)
   ↓
Private Resume Agent
   └─ extract_evidence (Gemma 4 Local via Ollama)
   ↓
Skill Builder
   ├─ deterministic_gap_analysis (Python)
   └─ generate_learning_plan (Gemini 1.5 Flash)
        """,
        language="text",
    )

    st.markdown("### Runtime Distribution")
    st.write("- **Job Scout:** ☁ Gemini / Vertex AI (`gemini-1.5-flash`)")
    st.write("- **Private Resume:** 🔒 Gemma 4 Local (`gemma4:12b` via `http://localhost:11434`)")
    st.write("- **Skill Builder:** ⚙ Python Deterministic + ☁ Gemini Reasoning")


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
