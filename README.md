# Agentic Career Lab

<p align="center">
  <b>A Privacy-First, Multi-Agent AI Career Assistant</b><br/>
  <i>Empowering students and job seekers with evidence-grounded career planning, local AI resume intelligence, and actionable upskilling.</i>
</p>

<p align="center">
  <a href="https://github.com/hastimal/agentic-career-lab/releases/tag/v0.10.2"><img src="https://img.shields.io/badge/Release-v0.10.2-blue.svg?style=flat-square" alt="Release v0.10.2"></a>
  <a href="https://github.com/hastimal/agentic-career-lab/blob/main/pyproject.toml"><img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://google.github.io/adk-docs/"><img src="https://img.shields.io/badge/Google%20ADK-Integrated-4285F4.svg?style=flat-square&logo=google&logoColor=white" alt="Google ADK"></a>
  <a href="https://ai.google.dev/gemma"><img src="https://img.shields.io/badge/Gemma%204-12B%20Local-10b981.svg?style=flat-square" alt="Local Gemma 4"></a>
  <a href="https://ollama.ai"><img src="https://img.shields.io/badge/Ollama-Offline%20First-000000.svg?style=flat-square" alt="Ollama"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="https://github.com/hastimal/agentic-career-lab/actions/workflows/ci.yml"><img src="https://img.shields.io/badge/CI-Passing-brightgreen.svg?style=flat-square" alt="CI Status"></a>
  <a href="https://github.com/hastimal/agentic-career-lab/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="MIT License"></a>
</p>

---

## 🌟 Executive Summary

**Agentic Career Lab** is an open-source, evidence-grounded career guidance platform designed for college students and technical job seekers. It pairs **Google ADK** multi-agent registration and tool adapters with **local Gemma 4** (`gemma4:12b` via native Ollama) for private resume analysis, providing structured roadmaps and real-time interactive actions through a modern **Streamlit** application.

---

## 📸 See It in Action

Real screenshots captured directly from the live application:

| **1. Student Dashboard** | **2. Ask Career AI Assistant** |
| :---: | :---: |
| [![Student Dashboard](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-dashboard.png)](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-dashboard.png)<br/><sub>*Quick actions, target role metrics, and persistent career journey tracking.*</sub> | [![Ask Career AI](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-agent-chat.png)](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-agent-chat.png)<br/><sub>*Streaming multi-turn guidance powered by local Gemma 4 with interactive action buttons.*</sub> |
| **3. Skill Gap Analysis** | **4. Guided Learning Plan** |
| [![Skill Gap Analysis](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-skill-gap-analysis.png)](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-skill-gap-analysis.png)<br/><sub>*Explainable 3-tier categorization: Demonstrated, Mentioned, and Missing skills.*</sub> | [![Guided Learning Plan](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-learning-plan.png)](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/ui-learning-plan.png)<br/><sub>*Tailored weekly roadmap across WATCH, LEARN, PRACTICE, and BUILD modalities.*</sub> |

> 📸 *For the complete inventory of all 10 verified application screens, see the [Screenshot Manifest](https://github.com/hastimal/agentic-career-lab/blob/main/docs/images/SCREENSHOT-MANIFEST.md).*

---

## 🏛️ How It Works

Agentic Career Lab coordinates specialist agents across clear boundaries. The Streamlit interface connects to the **CareerChatOrchestrator** and **Google ADK Coordinator**, dispatching domain tools across local and optional cloud environments.

![Multi-Agent Architecture](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/system-overview.svg)

### Verified Architecture Components:
- **Streamlit Application (`app.py`):** High-performance UI shell with real-time token streaming and navigation state machine.
- **Ask Career AI (`chat/`):** Conversational engine integrating progressive local Ollama streaming with grounded tool calling.
- **Google ADK Coordinator (`coordinator/adk_coordinator.py`):** Registers specialized specialist agents (`job_scout`, `private_resume_agent`, `skill_builder`) and exposes typed tool wrappers.
- **Job Scout Agent (`agents/job_scout/`):** Discovers verified opportunities and normalizes job requirements deterministically.
- **Private Resume Agent (`agents/resume_agent/`):** Evaluates uploaded resumes strictly in memory via local Gemma 4, enforcing factual grounding.
- **Skill Builder Agent (`agents/skill_builder/`):** Calculates requirement matches and maps missing skills to canonical resources.
- **Grounded Career Tools (`chat/tools.py`):** Typed adapters (`find_jobs`, `recommend_resources`, `explain_skill_gaps`) providing validated parameters.

> 💡 *For low-level container topology, Tempo tracing, and Prometheus metrics, see the [Docker & Observability Architecture](https://github.com/hastimal/agentic-career-lab/blob/main/docs/architecture.md).*

---

## 🔒 Privacy First

Privacy is a non-negotiable architectural boundary in Agentic Career Lab. We guarantee that your private documents remain strictly under your control.

![Privacy Boundary](https://raw.githubusercontent.com/hastimal/agentic-career-lab/main/docs/images/privacy-boundary.svg)

### Core Privacy Guarantees:
1. **Local-First Default:** All resume parsing, skill evidence extraction, and chat reasoning run on your host machine via Ollama (`gemma4:12b`).
2. **Zero Default Cloud Inference:** Cloud AI endpoints are completely disabled unless affirmative, recorded consent (`cloud_consent=True`) is explicitly granted.
3. **Strict Payload Allowlist:** When optional cloud planning is activated, the privacy guard transmits only high-level skill names and target titles. Raw resume text, personal contact information, and PDF bytes are **never** transmitted.
4. **Offline Fallback Engine:** If cloud consent is denied or external networks are unavailable, a deterministic Python planner generates comprehensive curricula directly from the local 104-item catalog.
5. **Sanitized Telemetry:** Observability traces (OpenTelemetry, Prometheus, Tempo) automatically redact prompts, completions, and student PII.

---

## 🎯 Key Features & Capabilities

- **💬 Multi-Turn "Ask Career AI":** Context-aware career mentor answering queries about readiness, missing skills, and interview preparation.
- **⚡ Real-Time Gemma 4 Streaming:** Progressive token streaming directly in Streamlit via native Ollama streaming (`httpx.stream`) with clear visual progress states.
- **🎮 5 Interactive Career Actions:**
  - `SELECT_JOB`: Binds an opportunity to your session and invalidates stale comparisons.
  - `OPEN_SKILL_GAP_ANALYSIS`: Routes directly to the evidence-based requirement breakdown.
  - `OPEN_LEARNING_RESOURCE`: Opens curated HTTPS resources directly from the 104-item catalog.
  - `CONTINUE_LEARNING`: Navigates to your next incomplete task in My Learning Plan.
  - `VIEW_CAREER_REPORT`: Opens the exportable comprehensive Markdown career summary.
- **🧭 Interactive Career Journey Tracker:** Clickable 3-stage progress tracker (`1. Job Selected` → `2. Resume Analyzed` → `3. Learning Plan Ready`).
- **📚 Curated 104-Resource Learning Catalog:** High-quality learning materials organized by modality:
  - 📺 **WATCH:** YouTube tutorials and architectural deep dives from engineering leaders.
  - 📖 **LEARN:** Official documentation, standard certification curricula, and textbooks.
  - 💻 **PRACTICE:** Interactive code katas, sandboxes, and cloud labs.
  - 🛠️ **BUILD:** Real-world capstone projects, open-source repositories, and portfolio deliverables.

---

## 🧭 Choose How to Run

Agentic Career Lab provides two officially supported ways to run:

| Feature / Mode | ⚡ Option A: Quick Start (`uvx`) | 🐳 Option B: Full Observability (Docker Compose) |
| :--- | :--- | :--- |
| **Best For** | Students, quick evaluations, offline local use | Architecture exploration, telemetry, multi-agent tracing |
| **Setup Time** | ~1 minute (no clone or build required) | ~3 minutes (containers build & start) |
| **Git Clone** | ❌ Not required | ✅ `git clone` required |
| **Docker Engine** | ❌ Not required | ✅ Docker Desktop or Docker Engine required |
| **Ollama** | ✅ Local host Ollama (`gemma4:12b`) | ✅ Host Ollama or optional containerized profile |
| **Telemetry Stack** | Console / local diagnostics only | ✅ OpenTelemetry Collector + Prometheus + Tempo + Grafana |
| **Complete Guide** | [Cross-Platform uvx Guide](https://github.com/hastimal/agentic-career-lab/blob/main/docs/installation/uvx.md) | [Docker Compose Observability Guide](https://github.com/hastimal/agentic-career-lab/blob/main/docs/installation/docker-compose.md) |

---

### Option A: Quick Start with `uvx` (Fastest, No Clone Needed)

Run the published application directly from PyPI in an isolated environment:

```bash
# 1. Verify prerequisites (Ollama & Gemma 4)
uvx agentic-career-lab doctor

# 2. Launch the interactive Streamlit application
uvx agentic-career-lab
```

*Requirements:* Install [uv](https://docs.astral.sh/uv/) and [Ollama](https://ollama.com), then pull `gemma4:12b`. No repository checkout or virtualenv creation is needed.

---

### Option B: Docker Compose with Full Observability (Tracing & Dashboards)

Run the complete multi-agent system alongside OpenTelemetry, Prometheus, Tempo, and Grafana:

```bash
# 1. Clone repository
git clone https://github.com/hastimal/agentic-career-lab.git
cd agentic-career-lab

# 2. Check the host before building — docker, uv, ollama and the model it serves,
#    the app port, and the container -> host route
scripts/setup.sh

# 3. Launch full observability stack
docker compose --profile observability up -d --build
```

- **Streamlit Web UI:** [http://localhost:8501](http://localhost:8501)
- **Grafana Dashboards:** [http://localhost:3000](http://localhost:3000) (pre-configured anonymous admin)
- **Prometheus Metrics:** [http://localhost:9090](http://localhost:9090)
- **Tempo Distributed Tracing:** [http://localhost:3200](http://localhost:3200)

---

## 💻 Install & Run — Windows, macOS, Linux (Cross-Platform CLI)

You can run **Agentic Career Lab** instantly on any desktop platform using [`uvx`](https://docs.astral.sh/uv/guides/tools/).

With `uvx`, you **do not** need to:
- ❌ Clone the Git repository
- ❌ Create a Python virtual environment manually
- ❌ Install Docker for standalone CLI mode

### 📋 Prerequisites
1. **[`uv` / `uvx`](https://docs.astral.sh/uv/)**: Fast Python package and tool runner (uv manages Python versions automatically).
2. **[Ollama](https://ollama.com)**: Local inference engine running offline on your host machine.
3. **`gemma4:12b` model**: Private, local AI model for resume intelligence and chat guidance.
4. **Internet connection**: Only required for the initial package download and model pull.

---

### 🪟 Windows (PowerShell)

**Step 1: Install `uv`** (using Windows Package Manager):
```powershell
winget install --id astral-sh.uv -e
```
*Alternative standalone installer:*
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 2: Restart PowerShell** so the new `PATH` entries take effect.

**Step 3: Verify installation:**
```powershell
uv --version
uvx --version
```

**Step 4: Install Ollama for Windows:**
Download and run the official installer from [https://ollama.com/download/windows](https://ollama.com/download/windows).

**Step 5: Pull local Gemma 4 model:**
```powershell
ollama pull gemma4:12b
```

**Step 6: Check readiness:**
```powershell
uvx agentic-career-lab doctor
```

**Step 7: Launch application:**
```powershell
uvx agentic-career-lab
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

### 🍎 macOS

**Step 1: Install `uv`:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*Restart your terminal if necessary to refresh your `PATH`.*

**Step 2: Verify `uvx`:**
```bash
uvx --version
```

**Step 3: Install Ollama for macOS:**
Download the native macOS app from [https://ollama.com/download/mac](https://ollama.com/download/mac).

**Step 4: Pull model, run diagnostics, and launch:**
```bash
ollama pull gemma4:12b
uvx agentic-career-lab doctor
uvx agentic-career-lab
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

### 🐧 Linux

**Step 1: Install `uv`:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*Verify `uvx --version` after reloading your shell.*

**Step 2: Install Ollama for Linux:**
Follow the official Linux installation command from [https://ollama.com/download/linux](https://ollama.com/download/linux):
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Step 3: Pull model, run diagnostics, and launch:**
```bash
ollama pull gemma4:12b
uvx agentic-career-lab doctor
uvx agentic-career-lab
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

### 📊 Cross-Platform Quickstart & Validation Matrix

| Platform | Install `uv` | Install Ollama | Pull Gemma 4 | Run Doctor | Launch App | Validation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **macOS (Apple Silicon / Intel)** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | [ollama.com/download/mac](https://ollama.com/download/mac) | `ollama pull gemma4:12b` | `uvx agentic-career-lab doctor` | `uvx agentic-career-lab` | **Verified** (Release Acceptance) |
| **Linux (Ubuntu / Debian / RHEL)** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | [ollama.com/download/linux](https://ollama.com/download/linux) | `ollama pull gemma4:12b` | `uvx agentic-career-lab doctor` | `uvx agentic-career-lab` | **Verified** (CI Suite & Docker) |
| **Windows 10/11 (PowerShell)** | `winget install --id astral-sh.uv -e` | [ollama.com/download/windows](https://ollama.com/download/windows) | `ollama pull gemma4:12b` | `uvx agentic-career-lab doctor` | `uvx agentic-career-lab` | **Partially Verified** (Package build/install verified; full local Gemma GPU acceptance requires host testing) |

> 📖 *For in-depth troubleshooting, PowerShell execution tips, and port configuration, see the [Cross-Platform uvx Installation Guide](https://github.com/hastimal/agentic-career-lab/blob/main/docs/installation/uvx.md).*

---

## 🚀 Alternative Launch Options

### Option A: Docker Compose Deployment
For full details on deploying with containerized services and OpenTelemetry, see the dedicated [Docker Compose Deployment Guide](https://github.com/hastimal/agentic-career-lab/blob/main/docs/installation/docker-compose.md).

```bash
# Start the full observability stack
docker compose --profile observability up -d --build
```

---

### Option B: Local Python Development

```bash
# 1. Install uv package manager (https://docs.astral.sh/uv/)
uv venv
source .venv/bin/activate
uv sync --all-extras

# 2. Run Streamlit locally
uv run streamlit run src/agentic_career_lab/app.py
```

---

## 🧪 Testing & Quality Gates

Every release is validated with automated unit tests, linter checks, and Playwright browser suites:

```bash
# Code style and formatting
uv run ruff check .
uv run ruff format --check .

# Fast unit & integration test suite (113 tests)
uv run pytest

# Automated Playwright browser verification across all 10 student workflows
uv run python scripts/test_browser_acceptance.py

# Automated Playwright verification of all 5 interactive chat actions
uv run python scripts/test_browser_actions.py
```

---

## 🗺️ Roadmap & Community

- **Latest Release:** [v0.10.2 Release Notes](https://github.com/hastimal/agentic-career-lab/releases/tag/v0.10.2)
- **Product Roadmap:** [Roadmap](https://github.com/hastimal/agentic-career-lab/blob/main/docs/ROADMAP.md) (v0.11.0 Resume Studio through v0.15.0 Learning Experience)
- **Contribution Guidelines:** [CONTRIBUTING.md](https://github.com/hastimal/agentic-career-lab/blob/main/CONTRIBUTING.md)
- **Security & Privacy Policy:** [SECURITY.md](https://github.com/hastimal/agentic-career-lab/blob/main/SECURITY.md)
- **Code of Conduct:** [CODE_OF_CONDUCT.md](https://github.com/hastimal/agentic-career-lab/blob/main/CODE_OF_CONDUCT.md)
- **Issue Tracker:** [GitHub Issues](https://github.com/hastimal/agentic-career-lab/issues)
- **Known Limitations:** [Known Issues](https://github.com/hastimal/agentic-career-lab/blob/main/docs/known-issues.md)

---

<p align="center">
  <sub>Built with ❤️ by Hastimal Jangid and community contributors. Distributed under the MIT License.</sub>
</p>
