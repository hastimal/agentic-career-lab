# Agentic Career Lab

A privacy-aware hybrid multi-agent career platform for students.

Planned stack:
- Gemini
- Vertex AI
- Google ADK
- Gemma 4 on Ollama
- Streamlit
- Docker
- Cloud Run
- OpenTelemetry

*(Screenshot/Demo section placeholder)*

---

## 🚀 Key Highlights

- **🔒 Local Privacy Boundary:** Resume processing, evidence extraction, and bullet suggestions run 100% locally via **Gemma 4** (`gemma4:12b`) using Ollama.
- **☁ Opportunity Intelligence:** Current internship and job opportunity search powered by **Google Gemini** on Vertex AI.
- **⚙ Deterministic Matching:** Grounded, explainable skill gap analysis without fake arbitrary percentages.
- **🎓 Student-First:** Tailored 4-week learning roadmaps and portfolio project recommendations.

---

## 🗺️ 8-Milestone Roadmap

- [x] **Milestone 1: Foundation + UI Shell** — Complete
- [x] **Milestone 2: Job Scout Agent** — Complete
- [x] **Milestone 3: Private Resume Agent with Gemma 4 + Ollama** — Complete
- [ ] **Milestone 4: Skill Builder Agent** — Planned
- [ ] **Milestone 5: Google ADK Multi-Agent Coordinator** — Planned
- [ ] **Milestone 6: Hybrid Gemini + Gemma Routing** — Planned
- [ ] **Milestone 7: Docker + Cloud Run Deployment** — Planned
- [ ] **Milestone 8: Evaluation & Observability** — Planned

---

## 🎯 Job Scout Agent (Milestone 2)

The Job Scout Agent provides evidence-backed opportunity matching:

- **Provider Abstraction**: Allows fetching opportunities securely (currently featuring a deterministic mock provider for testing).
- **Source Preservation**: Every opportunity is tied to a verifiable external source URL to eliminate hallucinated job postings.
- **Requirement Extraction**: Parses requirements securely from job descriptions.
- **Skill Normalization**: Translates equivalent terms (e.g., `GCP` to `Google Cloud`, `k8s` to `Kubernetes`).
- **Explainable Matching**: Categorizes requirements into `Demonstrated`, `Partial`, and `Missing` using deterministic validation rather than arbitrary percentages.

**Limitations**: Currently runs via deterministic execution and mock data for UI safety. Live provider API integrations arrive in later milestones.

```text
Student Profile
      |
      v
Job Scout
      |
      v
Opportunity Provider
      |
      v
Requirement Extraction
      |
      v
Skill Matching
      |
      v
Evidence-Backed Results
```

## 🔒 Private Resume Agent (Milestone 3)

The Private Resume Agent ensures privacy by analyzing resumes strictly via a local Gemma 4 model through Ollama.

- **Local Inference**: Raw resume text is **never** transmitted to Gemini or Vertex AI.
- **Evidence Extraction**: Identifies skills, technologies, and experience strictly present in the resume.
- **Requirement Mapping**: Maps extracted evidence against job requirements to flag missing gaps.
- **Deterministic Validation**: Guardrails ensure that AI-suggested rewrites do not hallucinate new metrics, skills, or employers.
- **Safe Fallback**: If Ollama is unavailable, the agent fails gracefully locally and will not invoke cloud models.

```text
Resume
   |
   v
Gemma 4 / Ollama
   |
   v
Evidence Extraction
   |
   v
Requirement Mapping
   |
   v
Resume Suggestions
   |
   v
Claim Validator
```

---

## 🛠️ Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/hastimal/agentic-career-lab.git
cd agentic-career-lab

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e ".[dev]"
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

### 3. Run Streamlit UI Shell

```bash
streamlit run src/agentic_career_lab/app.py
```

---

## 🧪 Testing & Linting

```bash
ruff check .
ruff format --check .
pytest
```
