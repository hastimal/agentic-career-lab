# Milestone 4 — Skill Builder Agent
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Turn job requirements and resume evidence into prioritized skill gaps, a learning roadmap, and a focused portfolio project.

## Goal
Turn job requirements and resume evidence into prioritized skill gaps, a learning roadmap, and a focused portfolio project.

## What This Milestone Adds
- deterministic gap analysis
- required vs preferred prioritization
- role-specific learning roadmap
- portfolio project recommendation
- Skill Builder UI

## What This Milestone Does NOT Add
- ADK orchestration
- central hybrid routing
- Cloud Run deployment
- observability

## Architecture
```text
Job Requirements
       +
Resume Evidence
       |
       v
Deterministic Gap Analysis
       |
       v
Gemini Explanation
       |
       v
Learning Roadmap
       |
       v
Portfolio Project
```

## Antigravity Command

```text
Continue from Agentic Career Lab on main.

IMPLEMENT MILESTONE 4 ONLY.

Do NOT implement:
- ADK orchestration
- hybrid routing
- Cloud Run
- observability

Goal:
Build the Skill Builder Agent.

Inputs:
- StudentProfile
- selected Opportunity
- Opportunity requirements
- ResumeEvidence

Output:
- demonstrated strengths
- partial evidence
- missing skills
- prioritized gaps
- learning roadmap
- one focused portfolio project

Implement deterministic comparison first.

Concept:
Requirements
-
Evidence
=
Skill Gaps

Use statuses:
- Demonstrated
- Partial
- Missing
- Not Required

Do not let Gemini perform exact comparisons that Python can do reliably.

Use Gemini/Vertex AI for:
- semantic equivalence where necessary
- explanations
- learning-plan synthesis
- portfolio-project recommendations

Example:

Target:
AI Engineering Intern

Demonstrated:
- Python
- SQL
- Docker

Important gaps:
- Vertex AI
- Google ADK
- Kubernetes

Create a 2-week or 4-week plan.

Each recommendation must explain why it matters for the selected role.

Avoid generic recommendations.

Recommend one portfolio project aligned with the selected opportunity.

Update Skill Builder UI with:
- Target Role
- Demonstrated Skills
- Partial Evidence
- Priority Gaps
- Learning Roadmap
- Portfolio Project

Tests:
- exact matches
- normalized aliases
- required vs preferred skills
- gap prioritization
- no irrelevant recommendation
- structured output

Run:
ruff check .
ruff format --check .
pytest

Recommended commit:
feat: add opportunity-driven skill builder agent

STOP AFTER MILESTONE 4.
```

## Verification
```bash
ruff check .
ruff format --check .
pytest
streamlit run src/agentic_career_lab/app.py
```

## Expected Result
- role-specific gaps appear
- learning plan is grounded in requirements
- recommended project is relevant

## Commit
feat: add opportunity-driven skill builder agent

## Status
Planned
