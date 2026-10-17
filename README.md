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

## 🏛️ System Architecture

![System Architecture](docs/images/system-architecture.svg)

---

## 🗺️ 8-Milestone Roadmap

- [x] **Milestone 1: Foundation + UI Shell** — Complete
- [x] **Milestone 2: Job Scout Agent** — Complete
- [x] **Milestone 3: Private Resume Agent with Gemma 4 + Ollama** — Complete
- [x] **Milestone 4: Skill Builder Agent** — Complete
- [x] **Milestone 5: Google ADK Multi-Agent Coordinator** — Complete
- [x] **Milestone 6: Hybrid Gemini + Gemma Routing** — Complete
- [x] **Milestone 7: Docker-First Application Distribution** — Complete
- [ ] **Milestone 8: Evaluation & Observability** — Planned


---

## 🔀 Hybrid Gemini + Gemma Privacy Routing (Milestone 6)

Milestone 6 provides a working end-to-end multi-agent career preparation demo enforcing strict data privacy boundaries:
- **Local Gemma 4 Inference**: Private resume parsing, evidence extraction, and suggestion validation run locally via Ollama (`gemma4:12b`). Raw resume content is never transmitted to cloud models.
- **Cloud Gemini Reasoning**: Generates customized learning plans and portfolio project recommendations with `gemini-3.6-flash` / `gemini-3.8-flash` via Vertex AI / Gemini API.
- **Explicit Cloud Consent**: Streamlit UI includes explicit student consent toggles before sharing sanitized skill gap metadata with cloud AI. Declining consent gracefully falls back to deterministic Python planning.
- **Google ADK Orchestration**: Sequences Job Scout, Private Resume Agent, and Skill Builder through typed boundaries and compiles the final Career Action Plan.

### Hybrid Multi-Agent Workflow
![Hybrid Agent Workflow](docs/images/hybrid-agent-workflow.svg)

### Strict Local vs. Cloud Privacy Boundary
![Privacy Boundary](docs/images/privacy-boundary.svg)

---

## 🔄 End-to-End Resume-to-Career-Plan Pipeline

![Resume to Career Plan Workflow](docs/images/resume-to-career-plan-workflow.svg)

---

## 🐳 Container & Deployment Architecture (Milestone 7 Preview)

![Docker Architecture](docs/images/docker-architecture.svg)

---

## 🎓 Google ADK Coordinator (Milestone 5)

Gemini reasons. Gemma handles private resume intelligence locally. Python verifies deterministic facts. Google ADK coordinates the workflow.

- **Orchestration**: Directs flow between Job Scout, Private Resume Agent, and Skill Builder.
- **Privacy Boundary**: Guarantees raw resume data remains strictly in local models while sharing only structured outputs with the coordinator.
- **Partial Failures**: Cleanly handles situations like an offline Ollama instance without destroying prior job scout sessions.

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

## 🛠️ Skill Builder Agent (Milestone 4)

The Skill Builder helps bridge the gap between your verified resume and the target role by producing an evidence-grounded learning plan.

- **Deterministic Gaps**: Uses standard Python logic to identify and prioritize gaps based on requirements and M3 evidence.
- **Priority Ranking**: Rules-based approach to score gaps (High/Medium/Low).
- **Practical Planning**: Recommends short 2 or 4-week learning plans combined with a custom portfolio project.
- **Privacy Focus**: Minimizes sharing by only generating plans from metadata, not raw resumes.

---

## 🐳 Docker Quick Start (Recommended)

Run the entire application with Docker Compose in a single command:

```bash
# 1. Clone the repository
git clone https://github.com/hastimal/agentic-career-lab.git
cd agentic-career-lab

# 2. Configure environment (optional overrides)
cp .env.example .env

# 3. Start the application
docker compose up -d
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

### Ollama Runtime Modes & Platform Guidance

- **macOS / Apple Silicon (M1/M2/M3/M4) [Recommended]**:
  Run Ollama natively on macOS (`brew install ollama` or via Ollama Desktop app) and pull Gemma 4:
  ```bash
  ollama run gemma4:12b
  ```
  The container connects automatically to `http://host.docker.internal:11434` with **full Metal GPU acceleration** (Docker Desktop for macOS does not support Metal GPU passthrough to Linux containers).

- **Linux / Standalone (Containerized Ollama)**:
  If running without native Ollama, start the containerized Ollama service using the standalone profile:
  ```bash
  docker compose --profile standalone up -d
  # Download Gemma 4 model into the persistent container volume:
  docker exec -it agentic-career-lab-ollama ollama pull gemma4:12b
  ```

- **Stopping the Application**:
  ```bash
  docker compose down
  ```

---

## 🛠️ Local Development Quick Start (Virtual Environment)

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
