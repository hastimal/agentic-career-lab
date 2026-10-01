This file contains the reproducible Antigravity implementation prompt used to build Milestone 1 of Agentic Career Lab.

# Milestone 1 — Foundation

You are working as the lead AI/cloud engineer on a new open-source project.

Repository name:

agentic-career-lab

Python package:

agentic_career_lab

Project title:

Agentic Career Lab

Project goal:

Build a production-oriented, educational, privacy-aware hybrid multi-agent career platform for college students.

The full future architecture will eventually use:

- Gemini
- Vertex AI
- Google ADK
- Gemma
- Ollama
- Streamlit
- Docker
- Cloud Run
- OpenTelemetry
- evaluation

However:

IMPLEMENT MILESTONE 1 ONLY.

Do not implement later milestones.

---

## Milestone 1 objective

Create a clean, typed, testable project foundation and a polished UI shell.

Milestone 1 should establish:

- repository structure,
- Python package structure,
- configuration,
- logging,
- domain models,
- test infrastructure,
- linting,
- Streamlit application shell,
- README,
- architecture documentation,
- clean extension points for future agents and model adapters.

Do NOT implement:

- real job search,
- Job Scout behavior,
- Gemma inference,
- Ollama integration,
- resume rewriting,
- Skill Builder logic,
- Google ADK orchestration,
- multi-agent workflows,
- hybrid routing,
- Cloud Run deployment,
- observability backend,
- evaluation framework.

---

## Technology

Use:

- Python 3.11+
- Streamlit
- Pydantic
- pytest
- ruff

Use type hints throughout.

Avoid unnecessary abstractions.

Do not introduce:

- CI/CD
- Secret Manager
- GKE
- Terraform
- unnecessary databases

---

## Repository structure

Create a clean project approximately like:

agentic-career-lab/
├── src/
│   └── agentic_career_lab/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── logging_config.py
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── coordinator/
│       │   ├── job_scout/
│       │   ├── resume/
│       │   └── skill_builder/
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── student.py
│       │   ├── opportunity.py
│       │   ├── resume.py
│       │   └── skill_gap.py
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── gemini.py
│       │   └── local.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   └── base.py
│       │
│       ├── services/
│       └── utils/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docs/
│   └── architecture.md
│
├── deployment/
├── scripts/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── Dockerfile

Do not create empty folders/files solely for appearance.

Only create placeholders when they establish a useful architectural boundary.

---

## Configuration

Support configuration placeholders for:

GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION
GEMINI_MODEL
OLLAMA_BASE_URL
GEMMA_MODEL

Use sensible defaults where appropriate.

Default Ollama URL:

http://localhost:11434

Default Gemma model:

gemma4:12b

These values are placeholders only in Milestone 1.

Do NOT call Gemini, Vertex AI, Gemma, or Ollama yet.

---

## Domain models

Create typed Pydantic models for the future workflow.

At minimum:

### StudentProfile

Include fields such as:

- major
- graduation_year
- skills
- interests
- preferred_roles
- location

### Opportunity

Include fields such as:

- id
- title
- company
- location
- description
- source_name
- source_url

### OpportunityRequirement

Include:

- name
- requirement_type
- evidence_text

### ResumeEvidence

Include:

- source_text
- category
- skills
- technologies

### SkillGap

Include:

- skill
- status
- reason
- priority

### LearningPlan

Include:

- target_role
- gaps
- weeks
- project_recommendation

Do not over-model fields we do not yet need.

---

## Model/provider interfaces

Create minimal abstract boundaries for future model integration.

Conceptually:

LLM client abstraction
Local LLM abstraction
Tool abstraction

Do not implement live calls.

The purpose is only to prevent future agents from being tightly coupled to model providers.

---

## Streamlit UI

Build a clean modern application shell.

Project name:

Agentic Career Lab

Tagline:

Find the opportunity.
Understand your gaps.
Build the skills.
Apply with confidence.

Navigation:

- Chat
- Opportunities
- Private Resume
- Skill Builder
- Agent Activity

The landing experience should include:

Agentic Career Lab

Find the opportunity.
Understand your gaps.
Build the skills.
Apply with confidence.

Quick actions:

[Find Internships]
[Analyze Resume]
[Build My Skills]

Show model architecture badges:

☁ Gemini / Vertex AI
🔒 Gemma Local

Make clear that these are architectural/future capabilities, not active inference yet.

---

## Chat page

Create a polished placeholder chat interface.

Include an example prompt such as:

"I'm a junior computer science student with Python, SQL, Docker and basic Google Cloud skills. Help me prepare for an AI/cloud internship."

Do not return fake AI responses.

Use demo/static explanatory state only.

---

## Opportunities page

Create a placeholder page explaining that Job Scout will be implemented in Milestone 2.

Do not show fake live job postings unless they are explicitly labeled demo/mock.

---

## Private Resume page

Create the future privacy story.

Display:

Private Resume Lab

🔒 Local AI Processing

Future behavior:
Resume analysis will use local Gemma so sensitive resume content does not need to be sent to a cloud model.

Do not implement Gemma inference yet.

---

## Skill Builder page

Create a static educational preview showing:

- demonstrated skills,
- future skill gaps,
- example 4-week learning plan structure.

Clearly label all content as example/demo content.

---

## Agent Activity page

Create a static architecture preview showing:

Career Coordinator
    ↓
Job Scout
Resume Agent
Skill Builder

Also show:

☁ Gemini / Vertex AI
🔒 Gemma Local
⚙ Deterministic Python

Do not implement actual execution tracing yet.

---

## README

README should explain:

1. What Agentic Career Lab is
2. Why the project exists
3. Who it is for
4. Planned architecture
5. Privacy-aware hybrid AI design
6. Repository structure
7. Local setup
8. Test commands
9. Future 8-milestone roadmap

Include an ASCII architecture diagram:

Student
   ↓
Career Coordinator
   │
   ├── Job Scout
   ├── Private Resume Agent
   └── Skill Builder

Future model strategy:

Job discovery
→ Gemini / Vertex AI

Resume processing
→ Gemma Local

Deterministic matching
→ Python

Do not make unsupported claims.

---

## Architecture documentation

Create:

docs/architecture.md

Explain:

- future multi-agent design,
- separation between cloud and local models,
- privacy boundary,
- why resume processing is intended to stay local,
- why deterministic Python should be used when LLM reasoning is unnecessary.

---

## Eight-milestone roadmap

Document:

1. Foundation
2. Job Scout Agent
3. Private Resume Agent with Gemma
4. Skill Builder Agent
5. Google ADK Coordinator
6. Hybrid Gemini + Gemma Routing
7. Docker + Cloud Run Deployment
8. Evaluation + Observability

Milestone 1 is the only milestone being implemented now.

---

## Testing

Add tests for:

- configuration defaults,
- core Pydantic models,
- validation,
- application imports,
- basic UI-support logic where appropriate.

Do not write tests that require:

- Google Cloud,
- Vertex AI,
- Ollama,
- internet access.

---

## Quality checks

Run:

ruff check .
ruff format --check .
pytest

If mypy is already configured, run:

mypy src

Do not claim anything passed unless it was actually executed.

---

## Run command

The application must run using:

streamlit run src/agentic_career_lab/app.py

Verify that command works.

---

## Git behavior

Do not create feature branches.

We are using main directly for this project sprint.

Do not push automatically unless explicitly requested.

At the end show:

1. files created/modified,
2. architecture implemented,
3. test results,
4. exact run command,
5. git status,
6. recommended commit message.

Recommended commit message:

feat: establish Agentic Career Lab foundation

STOP AFTER MILESTONE 1.

Do not begin Milestone 2.

---

Expected verification:
ruff check .
ruff format --check .
pytest
streamlit run src/agentic_career_lab/app.py
