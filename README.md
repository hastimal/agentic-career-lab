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
- [ ] **Milestone 2: Job Scout Agent** — Planned
- [ ] **Milestone 3: Private Resume Agent with Gemma 4 + Ollama** — Planned
- [ ] **Milestone 4: Skill Builder Agent** — Planned
- [ ] **Milestone 5: Google ADK Multi-Agent Coordinator** — Planned
- [ ] **Milestone 6: Hybrid Gemini + Gemma Routing** — Planned
- [ ] **Milestone 7: Docker + Cloud Run Deployment** — Planned
- [ ] **Milestone 8: Evaluation & Observability** — Planned

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
