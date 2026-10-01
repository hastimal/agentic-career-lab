# Milestone 6 — Hybrid Gemini + Gemma 4 Model Routing
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Add explicit privacy-aware routing across Gemini, Gemma 4, deterministic Python, and external tools.

## Goal
Add explicit privacy-aware routing across Gemini, Gemma 4, deterministic Python, and external tools.

## What This Milestone Adds
- typed routing policy
- privacy-aware model selection
- local/cloud separation
- sanitized routing metadata
- safe fallback behavior

## What This Milestone Does NOT Add
- Cloud Run deployment
- observability backend
- extra specialist agents

## Architecture
```text
Task
 |
 v
Routing Policy
 +--> Fresh/current info -> Gemini / Vertex AI
 +--> Private resume     -> Gemma 4 / Ollama
 +--> Exact comparison   -> Python
 +--> Tool execution     -> External provider
```

## Antigravity Command

```text
Continue from Agentic Career Lab on main.

IMPLEMENT MILESTONE 6 ONLY.

Create an explicit routing layer.

Do not let each agent choose models ad hoc.

Routing rules:

Fresh/current opportunity information
-> search provider + Gemini / Vertex AI

Agent orchestration
-> Google ADK

Sensitive resume analysis
-> Gemma 4 through local Ollama

Exact skill comparison
-> deterministic Python

Learning-plan explanation
-> Gemini where useful

Create typed routing decisions.

Capture sanitized metadata:
- task_type
- selected_runtime
- selected_model
- reason
- latency
- status

Never log raw resume text.

Critical privacy rule:

If Gemma 4/Ollama is unavailable:
DO NOT automatically send resume text to Gemini.

Return:
Private resume analysis unavailable because the local model is offline.

Add visible UI badges:
Gemini / Vertex AI
Gemma 4 / Ollama
Deterministic Python

Tests:
- resume routes local
- current job reasoning routes cloud
- exact matching routes Python
- local failure does not trigger cloud resume fallback
- routing metadata is sanitized

Run:
ruff check .
ruff format --check .
pytest

Recommended commit:
feat: add privacy-aware hybrid model routing

STOP AFTER MILESTONE 6.
```

## Verification
```bash
ruff check .
ruff format --check .
pytest
streamlit run src/agentic_career_lab/app.py
```

## Expected Result
- model routing is explicit
- privacy boundaries are enforced
- failures are visible and safe

## Commit
feat: add privacy-aware hybrid model routing

## Status
Planned
