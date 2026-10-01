# Milestone 8 — Evaluation + OpenTelemetry Observability
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Add practical evaluation, tracing, and production insight for the complete hybrid multi-agent workflow.

## Goal
Add practical evaluation, tracing, and production insight for the complete hybrid multi-agent workflow.

## What This Milestone Adds
- evaluation fixtures
- routing evaluation
- skill-match evaluation
- unsupported-claim evaluation
- OpenTelemetry instrumentation
- sanitized execution metadata
- improved Agent Activity UI

## What This Milestone Does NOT Add
- mandatory Grafana
- mandatory Tempo
- a complex observability platform
- raw resume logging

## Architecture
```text
User Request
     |
     v
Coordinator
     |
     v
Agent
     |
     v
Tool / Model
     |
     v
Response

     |
     v
OpenTelemetry
     |
     +--> latency
     +--> routing
     +--> tool status
     +--> model runtime
     +--> failures
```

## Antigravity Command

```text
Continue from Agentic Career Lab on main.

IMPLEMENT MILESTONE 8 ONLY.

Goal:
Add practical evaluation and lightweight observability.

Do not overbuild.

Create evaluation fixtures for at least:

STUDENT A

Profile:
Junior CS student

Skills:
- Python
- SQL
- Docker
- basic Google Cloud

Target:
AI/cloud internship

Expected behavior:
The system should recognize demonstrated backend/cloud fundamentals and identify relevant AI/cloud gaps without inventing experience.

STUDENT B

Profile:
Freshman

Skills:
- basic Python

Expected behavior:
The system must not pretend this student has advanced cloud, AI, infrastructure, or production experience.

STUDENT C

Profile:
Graduate data science student

Skills:
- Python
- PyTorch
- GCP

Expected behavior:
More advanced AI/ML opportunities may be appropriate when supported by actual job requirements.

Evaluate:
- requirement extraction
- skill normalization
- skill matching
- resume evidence accuracy
- unsupported claim detection
- routing correctness
- tool success
- explanation quality
- latency

Add lightweight OpenTelemetry instrumentation around:

request
-> coordinator
-> agent
-> tool
-> model
-> response

Record:
- agent name
- tool name
- model runtime
- latency
- status
- failure information

Never record raw resume text.
Never record unnecessary PII.

Update Agent Activity UI.

Show information conceptually like:

Career Coordinator
   |
   v
Job Scout
   +--> search_opportunities
   +--> extract_requirements
   |
   v
Private Resume Agent
   +--> Gemma 4 / Ollama
   |
   v
Skill Builder
   +--> create_learning_plan

Models:
Gemini / Vertex AI
Gemma 4 / Ollama
Python

Execution:
- agents used
- tools used
- model runtimes
- total latency
- status

Do NOT add Grafana or Tempo unless they are already trivial to integrate and clearly useful.

Structured logging + OpenTelemetry is enough for this milestone.

Update README with:
- final architecture
- privacy boundary
- local mode
- cloud mode
- evaluation approach
- observability approach
- known limitations
- future work

Run:
ruff check .
ruff format --check .
pytest

Run the evaluation suite.

Recommended commit:
feat: add agent evaluation and observability

STOP AFTER MILESTONE 8.
```

## Verification
```bash
ruff check .
ruff format --check .
pytest
```

## Expected Result
- evaluation cases run
- routing behavior can be inspected
- agent/tool/model timing is observable
- no raw resume content is logged
- Agent Activity is explainable

## Commit
feat: add agent evaluation and observability

## Status
Planned
