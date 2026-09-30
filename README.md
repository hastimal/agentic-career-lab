# Agentic Career Lab

A privacy-aware hybrid multi-agent career platform for college students.

```text
Student
   ↓
Career Coordinator — Google ADK
   │
   ├── Job Scout Agent
   │      └── Gemini / Vertex AI + job search tools
   │
   ├── Private Resume Agent
   │      └── Gemma 4 via local Ollama
   │
   └── Skill Builder Agent
          └── Gemini / deterministic Python as appropriate
```

---

## 🚀 Key Highlights

- **🔒 Local Privacy Boundary:** Resume processing, evidence extraction, and bullet suggestions run 100% locally via **Gemma 4** (`gemma4:12b`) using Ollama.
- **☁ Opportunity Intelligence:** Current internship and job opportunity search powered by **Google Gemini** on Vertex AI.
- **⚙ Deterministic Matching:** Grounded, explainable skill gap analysis without fake arbitrary percentages.
- **🎓 Student-First:** Tailored 4-week learning roadmaps and portfolio project recommendations.

---

## 🗺️ 8-Milestone Roadmap

- [x] **Milestone 1: Foundation + UI Shell** — Core models, configuration, Streamlit AI workspace UI.
- [ ] **Milestone 2: Job Scout Agent** — Opportunity provider abstraction, normalization, verified source extraction.
- [ ] **Milestone 3: Private Resume Agent (Gemma 4 + Ollama)** — Local resume evidence parsing and guardrails against fabricated claims.
- [ ] **Milestone 4: Skill Builder Agent** — Deterministic requirement/evidence comparison & personalized learning roadmaps.
- [ ] **Milestone 5: Google ADK Multi-Agent Coordinator** — State orchestration across specialist agents.
- [ ] **Milestone 6: Hybrid Gemini + Gemma Routing** — Privacy-aware model routing and offline fallbacks.
- [ ] **Milestone 7: Docker + Cloud Run Deployment** — Cloud Run deployment with local/cloud execution modes.
- [ ] **Milestone 8: Light Evaluation + Observability** — Student test fixtures, OpenTelemetry traces, and latency analysis.

---

## 🛠️ Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/your-username/agentic-career-lab.git
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
