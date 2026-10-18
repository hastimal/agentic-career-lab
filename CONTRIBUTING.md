# Contributing to Agentic Career Lab

Welcome to the **Agentic Career Lab** community! We are excited to collaborate with builders, researchers, students, and engineers working on open-source, privacy-first career agency.

This document outlines how to set up your local development environment, project architecture, engineering rules, testing practices, and our pull request guidelines.

---

## 🔒 Core Principles & Privacy Boundaries

Before submitting code, please understand the non-negotiable architectural constraints of Agentic Career Lab:

1. **Local-First Privacy by Default:**
   - Default inference runs via local Google Gemma 4 on [Ollama](https://ollama.ai) (`gemma4:12b`).
   - Uploaded resumes and student conversation transcripts **must never be dispatched to cloud endpoints** without explicit, affirmative user consent (`cloud_consent=True`).
   - Telemetry (OpenTelemetry, Prometheus, Tempo) and logs **must never capture** raw resume text, student PII, prompts, or LLM-generated completions.
2. **Evidence-Based Grounding:**
   - Skills, gaps, and recommendations must be grounded in verified resume text or curated catalog items.
   - Do **not** hallucinate qualifications or promote unverified resume keywords into verified demonstrated skills.
   - Generative career suggestions must be clearly distinguished from deterministic system actions.
3. **No Unsolicited Architecture Shifts:**
   - The user application is built with **Streamlit** and Python 3.11+. Do not introduce alternative frontends or databases without a prior approved design issue.

---

## 🛠️ Local Development Setup

### Prerequisites

- **Python 3.11+**
- **uv**: Fast Python package manager ([installation instructions](https://docs.astral.sh/uv/))
- **Docker & Docker Compose**: For containerized runtime and telemetry (Prometheus, Grafana, Tempo, OpenTelemetry Collector)
- **Ollama**: Native host installation with `gemma4:12b` model pulled:
  ```bash
  ollama pull gemma4:12b
  ollama serve
  ```

### 1. Clone the Repository

```bash
git clone https://github.com/hastimal/agentic-career-lab.git
cd agentic-career-lab
```

### 2. Install Python Dependencies with `uv`

```bash
# Create virtual environment and sync dependencies (including dev and test tools)
uv venv
source .venv/bin/activate
uv sync --all-extras
```

### 3. Install Playwright Browsers (for end-to-end testing)

```bash
uv run playwright install chromium
```

### 4. Running the Application Locally

#### Option A: Running with Native Python (Fastest for UI and Agent Tweaks)

Ensure Ollama is running (`ollama serve`). Then start Streamlit:

```bash
uv run streamlit run src/agentic_career_lab/app.py
```

Open `http://localhost:8501` in your browser.

#### Option B: Running with Docker Compose (Full Telemetry Stack)

To run the complete production environment including OpenTelemetry Collector, Prometheus, Tempo, and Grafana:

```bash
# Build and run the stack
docker compose build app
docker compose up -d

# Verify container health
docker compose ps
curl http://localhost:8501/_stcore/health
```

- **Streamlit App:** `http://localhost:8501`
- **Grafana Dashboards:** `http://localhost:3000` (admin / admin)
- **Prometheus:** `http://localhost:9090`

---

## 🏛️ Architecture Overview

```text
src/agentic_career_lab/
├── agents/                    # Multi-agent implementations
│   ├── coordinator.py         # Google ADK career coordinator
│   ├── job_scout/             # Opportunity discovery and provider abstraction
│   ├── resume_agent/          # Private local resume parsing and evidence extraction
│   └── skill_builder/         # Evidence-based skill gap analyzer
├── chat/                      # v0.10.0 Ask Career AI subsystem
│   ├── models.py              # ChatAction, ChatMessage, ConversationState contracts
│   ├── orchestrator.py        # Multi-turn context management and tool dispatching
│   ├── privacy.py             # CareerChatPrivacyGuard and payload allowlisting
│   └── tools.py               # Grounded tools adapter mapping ADK actions
├── llm/                       # LLM clients & streaming adapters (Ollama, Gemini)
├── resources/                 # Canonical learning catalog (104+ curated items)
├── app.py                     # Streamlit frontend application
└── ui_helpers.py              # Visual styling, badge components, telemetry helpers
```

---

## 🧪 Testing & Code Quality Gates

All contributions must pass automated linting, formatting checks, and the unit/browser test suite before being reviewed.

### 1. Code Formatting & Linting (Ruff)

We use [Ruff](https://docs.astral.sh/ruff/) for Python formatting and linting:

```bash
# Check code style and rules
uv run ruff check .

# Check formatting
uv run ruff format --check .

# Auto-fix formatting or trivial lints
uv run ruff format .
uv run ruff check --fix .
```

### 2. Unit & Integration Tests (Pytest)

Run the fast unit test suite:

```bash
uv run pytest
```

### 3. Automated Browser Acceptance Tests (Playwright)

Run the complete 10-stage student journey acceptance suite and the 5 interactive chat action flows against a running instance:

```bash
# Test full 10-stage career journey
uv run python scripts/test_browser_acceptance.py

# Test 5 Ask Career AI interactive actions
uv run python scripts/test_browser_actions.py
```

---

## 🚀 Submitting a Pull Request (PR)

1. **Find or Open an Issue:** Check the [GitHub Issues](https://github.com/hastimal/agentic-career-lab/issues) or [Roadmap](docs/ROADMAP.md) before starting major work.
2. **Create a Topic Branch:**
   ```bash
   git checkout -b feat/your-feature-name
   # or fix/your-bugfix-name
   ```
3. **Commit Your Changes:** Write descriptive, imperative commit messages (e.g., `feat(resume): add docx export support`).
4. **Run Pre-Commit Verification:**
   ```bash
   git diff --check
   uv run ruff check .
   uv run ruff format --check .
   uv run pytest
   ```
5. **Open a Pull Request:** Target the `main` branch. Fill out the provided [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) completely, including verification steps and privacy impact.

---

## ⚖️ Review and Acceptance Standards

- **Maintain Privacy Guarantees:** Any PR introducing network requests must provide explicit confirmation that raw student data is protected.
- **Test Coverage:** All new features or bug fixes must include corresponding unit tests in `tests/`.
- **Grounded AI:** Features utilizing generative responses must handle local model timeouts, fallback states, and avoid fabricating claims.
