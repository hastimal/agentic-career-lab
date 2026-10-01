# Milestone 5 — Google ADK Multi-Agent Coordinator
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Use Google ADK to coordinate Job Scout, Private Resume Agent, and Skill Builder while preserving structured state and privacy boundaries.

## Goal
Use Google ADK to coordinate Job Scout, Private Resume Agent, and Skill Builder while preserving structured state and privacy boundaries.

## What This Milestone Adds
- Google ADK integration
- coordinator agent
- specialist routing
- structured state passing
- partial failure behavior
- agent activity stream

## What This Milestone Does NOT Add
- Interview Agent
- Cover Letter Agent
- Networking Agent
- central hybrid routing policy
- Cloud Run deployment
- observability backend

## Architecture
```text
                    Career Coordinator
                       Google ADK
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
     Job Scout         Resume Agent      Skill Builder
          |                 |                 |
 Gemini/Vertex AI     Gemma 4/Ollama     Gemini/Python
```

## Antigravity Command

```text
Continue from Agentic Career Lab on main.

IMPLEMENT MILESTONE 5 ONLY.

Integrate Google ADK.

Use one coordinator and exactly three specialist agents:
- Job Scout
- Private Resume Agent
- Skill Builder

Do not add:
- Interview Agent
- LinkedIn Agent
- Cover Letter Agent
- Networking Agent
- Salary Agent

Coordinator responsibilities:
- understand intent
- invoke required specialist agents
- pass structured state
- preserve evidence
- handle partial failures
- avoid circular delegation

Expected routing:

"Find internships"
-> Job Scout

"Analyze my resume"
-> Resume Agent

"What skills am I missing?"
-> Skill Builder

"Find a role and help me prepare"
-> Job Scout
-> Resume Agent if available
-> Skill Builder

Raw resume text must never be sent to cloud agents.

Resume Agent remains local.

Pass only sanitized/structured outputs when needed.

Preserve:
- opportunity source
- requirements
- resume evidence
- skill gaps
- learning plan

Create a sanitized activity stream for UI.

Handle failure safely.

If Ollama is unavailable:
- Job Scout can continue
- Skill Builder can continue where possible
- Resume analysis must be marked unavailable
- do not silently send the resume to Gemini

Update Chat UI for orchestration.

Update Agent Activity UI.

Tests:
- routing
- structured state passing
- local resume privacy
- partial failure
- no circular delegation

Run:
ruff check .
ruff format --check .
pytest

Recommended commit:
feat: orchestrate career workflow with Google ADK

STOP AFTER MILESTONE 5.
```

## Verification
```bash
ruff check .
ruff format --check .
pytest
streamlit run src/agentic_career_lab/app.py
```

## Expected Result
- multi-agent routing works
- agents delegate correctly
- private resume boundary is preserved

## Commit
feat: orchestrate career workflow with Google ADK

## Status
Planned
