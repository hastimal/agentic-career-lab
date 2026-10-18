# v0.10.0 Manual Acceptance Checklist & Testing Guide

This document defines the step-by-step verification checklist for the v0.10.0 "Ask Career AI" Chatbox, 5 Interactive Career Actions, Local Gemma 4 Streaming, and Privacy Boundaries in **Agentic Career Lab**.

---

## 🎯 Verification Matrix

| Area | Feature | Expected Behavior | Status |
| :--- | :--- | :--- | :---: |
| **Chat** | Ask Career AI UI | Streamlit chat shell with real-time streaming, suggested prompt chips, and multi-turn state. | ✅ Pass |
| **Chat** | Local Gemma 4 Streaming | Streamed token-by-token generation from local `gemma4:12b` via Ollama without cloud calls. | ✅ Pass |
| **Chat** | ADK Tool Execution | Deterministic execution of specialized career tools (`find_jobs`, `recommend_resources`, etc.). | ✅ Pass |
| **Action** | `SELECT_JOB` Action | Selects job from chat results, invalidates stale analyses, and navigates to My Resume. | ✅ Pass |
| **Action** | `OPEN_LEARNING_RESOURCE` Action | Direct `https://` link button to verified ResourceCatalog resource without leaking PII. | ✅ Pass |
| **Action** | `CONTINUE_LEARNING` Action | Inspects active learning plan, identifies next task, and navigates to My Learning Plan. | ✅ Pass |
| **Action** | `VIEW_CAREER_REPORT` Action | Validates workflow prerequisites and navigates to Career Report with Markdown export. | ✅ Pass |
| **Action** | `OPEN_SKILL_GAP_ANALYSIS` Action | Navigates to verified evidence-based Demonstrated vs Mentioned vs Missing skill breakdown. | ✅ Pass |
| **Tracker** | Career Journey Progress Tracker | Clickable 3-stage tracker on all major student pages (Job Selected, Resume Analysis, Learning Plan). | ✅ Pass |
| **Tracker** | Stage Invalidation on Job Change | Changing target opportunity invalidates stale resume analyses and roadmaps. | ✅ Pass |
| **Profile** | Dedicated "My Profile" Page | Manage education level, graduation year, location, target role, and self-reported skills. | ✅ Pass |
| **Profile** | Skill Integrity Distinction | Clean visual separation between self-reported profile skills and resume-verified skills. | ✅ Pass |
| **Privacy** | Cloud AI Consent Default | Unchecked by default (`False`). | ✅ Pass |
| **Privacy** | Consent Declined | 100% local deterministic execution. Zero calls to Gemini / Vertex AI. | ✅ Pass |
| **Privacy** | Telemetry Sanitization | Zero raw resume text, contact info, prompts, or completions in spans. | ✅ Pass |
| **Learning** | Verified Multi-Modal Catalog | WATCH, LEARN, PRACTICE, and BUILD categories with canonical IDs and verified links. | ✅ Pass |
| **Learning** | Compact Resource Cards | Clean dark cards with small provider icons (24–32px), title, metadata chips, and action buttons. | ✅ Pass |
| **Reporting** | Markdown Report Export | Generates structured `.md` career action plan with gap summary. | ✅ Pass |
| **Diagnostics**| User vs Developer Split | Student timeline visible; raw telemetry traces collapsed under diagnostics. | ✅ Pass |

---

## 📋 Step-by-Step Manual Walkthrough

### Step 1: Start Application
```bash
docker compose --profile observability up -d
```
Open **[http://localhost:8501](http://localhost:8501)**.

### Step 2: Dashboard & Quick Actions
1. Notice the hero banner and 3 workflow progress cards (`1. Target Opportunity`, `2. Private Resume Analysis`, `3. Learning Roadmap`).
2. Test the **⚡ Quick Actions**:
   - **Set Up My Profile**: Navigates directly to the dedicated My Profile page.
   - **Find Matching Jobs**: Navigates to Job Explorer with prefilled search values from your profile.
   - **Compare My Resume**: Prompts user if no opportunity selected, or navigates to My Resume.
   - **Identify My Top 3 Skill Gaps**: Guides user when prerequisites are missing or navigates to Skill Gap Analysis.

### Step 3: My Profile & Skill Integrity
1. Navigate to **My Profile** from the sidebar or Dashboard.
2. Edit Field of study, Education level, Graduation year, Preferred location, Target career role, and Current skills.
3. Click **💾 Save Profile** to persist state across navigation.
4. Click **🔄 Load Demo Student Profile (Alex Chen)** to verify demo loading.
5. Review the **Skills Integrity & Verification Breakdown** (self-reported vs resume-verified skills).

### Step 4: Job Explorer
1. Navigate to **Job Explorer**.
2. Notice the search fields (`Target Role`, `Location`, `Key Skills`) are prefilled from your active profile.
3. Check the badge labeled `DEMO DATA` or `LIVE`.
4. Click **Prepare My Resume** on any opportunity.

### Step 5: My Resume (Local Processing)
1. Either upload a PDF/DOCX or click **Load Demo Resume (Alex Chen)**.
2. If native Ollama (`gemma4:12b`) is running, click **Analyze Resume Privately**.
3. Check the extracted skills table: verify **no literal `\n` characters** are present.
4. Notice the privacy callout confirming processing occurred 100% locally on your device.

### Step 6: Skill Gap Analysis
1. Navigate to **Skill Gap Analysis**.
2. Observe the breakdown:
   - **Demonstrated Strengths**: Shows matching resume skills with supporting evidence.
   - **Mentioned / Partially Evidenced**: Explains why a mentioned skill is not yet demonstrated.
   - **Missing Requirements**: Explicitly lists missing technologies with learning guidance.

### Step 7: Learning Hub (Curated 104-Resource Technical Catalog)
1. Navigate to **Learning Hub**.
2. Filter resources by missing skill (e.g., `Kubernetes`, `Google Cloud`, `Docker`, `Vertex AI`).
3. Filter by difficulty (`Beginner`, `Intermediate`, `Advanced`).
4. Filter by resource type (`Video / Talk`, `Course`, `Documentation`, `Hands-on Lab`, `GitHub Project`).
5. Filter by provider (e.g., `Google Cloud`, `TechWorld with Nana`, `freeCodeCamp.org`, `Docker Inc.`).
6. Filter by access tier (`Free`, `Free Tier`, `Free Tier / Credits`).
7. Click on any resource link to verify destination validity.
8. Confirm resources clearly state provider, duration, prerequisites, and practical projects.

### Step 8: My Learning Plan (Guided Learning Experience & Dual Progress)
1. Navigate to **My Learning Plan**.
2. Select **2 Weeks (Fast Track)** or **4 Weeks (Comprehensive)**.
3. Observe the **Privacy & Cloud AI Sharing** box:
   - Verify the checkbox is **unchecked by default**.
   - Note the text: *"Consent is optional. When disabled, your plan is generated 100% locally with zero cloud API calls."*
4. Click **Generate Learning Roadmap**.
5. Verify the generated plan has **the exact number of weeks selected** (2 weeks = 2 weeks; 4 weeks = 4 weeks).
6. Under each week, explore the four guided modalities:
   - **📺 WATCH**: Curated YouTube tutorials and technical demos.
   - **📖 LEARN**: Structured courses, certification paths, and official documentation.
   - **💻 PRACTICE**: Interactive hands-on labs and tutorials.
   - **🛠️ BUILD**: GitHub reference projects and capstone architecture examples.
7. Test the **Weekly Action Tasks & Evidence**:
   - Check off an activity checkbox.
   - Click **Open Resource** to review linked study material (does not auto-complete the task).
   - Enter student deliverable / evidence link in the evidence field.
   - Notice the **Weekly Progress badge** and **Overall Activity Completion bar** update dynamically while leaving the Career Journey Progress Tracker independent at 100%.


### Step 8: Career Report
1. Navigate to **Career Report**.
2. Review the structured summary combining resume profile, selected role, skill gaps, and learning roadmap.
3. Click **Download Career Plan (.md)** to verify file export.

### Step 9: Activity & Diagnostics
1. Navigate to **Activity & Diagnostics**.
2. View the **Student Activity Timeline** (shows milestones like *Job Selected*, *Resume Analyzed*, *Skill Gaps Identified*, *Plan Generated*).
3. Expand **Advanced Telemetry & Diagnostics (Developers)** to inspect OpenTelemetry span events, trace IDs, and planner mode.

### Step 10: Grafana Observability
1. Open **[http://localhost:3000](http://localhost:3000)** (Grafana).
2. Open the **Agentic Career Lab** dashboard.
3. Verify metrics and TraceQL queries:
   - **TraceQL Query**: `{resource.service.name = "agentic-career-lab"}`
   - Verify recent workflow traces appear in Tempo and Explore.

---

## 🔒 Automated Verification Commands

Run the full verification suite anytime:

```bash
# 1. Syntax & Style Checks
uv run ruff check .
uv run ruff format --check .

# 2. Git Diff Check
git diff --check

# 3. Automated Test Suite (70 tests)
uv run pytest
```
