# Milestone 1 — Foundation
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Establish the typed Python foundation, Streamlit UI shell, configuration, tests, and architecture boundaries for the future hybrid multi-agent system.

## Goal
Establish the typed Python foundation, Streamlit UI shell, configuration, tests, and architecture boundaries for the future hybrid multi-agent system.

## What This Milestone Adds
- Python package foundation
- Streamlit UI shell
- typed domain models
- configuration
- logging
- tests
- README
- architecture documentation
- extension points for future agents and model providers

## What This Milestone Does NOT Add
- live job search
- live Gemini calls
- Gemma 4 inference
- Ollama integration
- Google ADK orchestration
- Skill Builder logic
- Cloud Run deployment
- observability

## Architecture
```text
Student
   |
   v
Streamlit UI
   |
   v
Future Agent Boundaries
   |
   +--> Job Scout
   +--> Private Resume Agent
   +--> Skill Builder

Future providers:
Gemini / Vertex AI
Gemma 4 / Ollama
Python tools
```

## Antigravity Command

```text
You are working as the lead AI/cloud engineer on a new open-source project.

Repository:
agentic-career-lab

Python package:
agentic_career_lab

Project title:
Agentic Career Lab

Project goal:
Build a production-oriented, educational, privacy-aware hybrid multi-agent career platform for college students.

Future technologies:
- Gemini
- Vertex AI
- Google ADK
- Gemma 4
- Ollama
- Streamlit
- Docker
- Cloud Run
- OpenTelemetry
- evaluation

IMPLEMENT MILESTONE 1 ONLY.

Create a clean, typed, testable project foundation.

Use:
- Python 3.11+
- Streamlit
- Pydantic
- pytest
- ruff
- type hints

Create approximately:

src/agentic_career_lab/
├── __init__.py
├── app.py
├── config.py
├── logging_config.py
├── agents/
│   ├── coordinator/
│   ├── job_scout/
│   ├── resume/
│   └── skill_builder/
├── models/
├── llm/
├── tools/
├── services/
└── utils/

tests/
docs/
deployment/
scripts/
.env.example
.gitignore
pyproject.toml
README.md
Dockerfile

Do not create useless empty files only for appearance.

Create typed Pydantic models for:
- StudentProfile
- Opportunity
- OpportunityRequirement
- ResumeEvidence
- SkillGap
- LearningPlan

Configuration placeholders:
GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION
GEMINI_MODEL
OLLAMA_BASE_URL
GEMMA_MODEL

Defaults:
OLLAMA_BASE_URL=http://localhost:11434
GEMMA_MODEL=gemma4:12b

Do NOT call Gemini, Vertex AI, Gemma 4, or Ollama yet.

Create minimal provider/model abstractions for future use.

Build Streamlit navigation:
- Chat
- Opportunities
- Private Resume
- Skill Builder
- Agent Activity

Landing page:

Agentic Career Lab

Find the opportunity.
Understand your gaps.
Build the skills.
Apply with confidence.

Quick actions:
[Find Internships]
[Analyze Resume]
[Build My Skills]

Show future architecture badges:
Gemini / Vertex AI
Gemma 4 Local / Ollama

Clearly label demo/static content.

Create README.md covering:
- project purpose
- architecture
- privacy-aware hybrid design
- local setup
- tests
- roadmap

Create docs/architecture.md covering:
- future multi-agent architecture
- Gemini vs Gemma 4 responsibilities
- local vs cloud boundaries
- deterministic Python use

Document roadmap:
1. Foundation
2. Job Scout
3. Private Resume with Gemma 4 + Ollama
4. Skill Builder
5. Google ADK Coordinator
6. Hybrid Gemini + Gemma 4 Routing
7. Cloud Run Deployment
8. Evaluation + Observability

Add tests for:
- configuration defaults
- domain models
- validation
- application imports

Tests must not require:
- internet
- Google Cloud
- Vertex AI
- Ollama

Run:
ruff check .
ruff format --check .
pytest

Verify:
streamlit run src/agentic_career_lab/app.py

Do not create feature branches.
Use main directly.

Do not push automatically.

Recommended commit:
feat: establish Agentic Career Lab foundation

STOP AFTER MILESTONE 1.
```

## Verification
```bash
ruff check .
ruff format --check .
pytest
streamlit run src/agentic_career_lab/app.py
```

## Expected Result
- app opens
- navigation works
- domain models exist
- architecture boundaries exist
- no live model calls are active

## Commit
feat: establish Agentic Career Lab foundation

## Status
Complete
