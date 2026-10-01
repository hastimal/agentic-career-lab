# Milestone 3 — Private Resume Agent with Gemma 4 + Ollama
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Add local privacy-aware resume analysis using Gemma 4 through Ollama with strict evidence and no-fabrication guardrails.

## Goal
Add local privacy-aware resume analysis using Gemma 4 through Ollama with strict evidence and no-fabrication guardrails.

## What This Milestone Adds
- local Gemma 4 model adapter
- Ollama connectivity
- resume evidence extraction
- job-to-resume evidence mapping
- safe bullet refinement
- deterministic unsupported-claim checks
- private resume UI

## What This Milestone Does NOT Add
- Skill Builder
- Google ADK orchestration
- hybrid routing policy
- Cloud Run support for local Ollama
- observability

## Architecture
```text
Resume
   |
   v
Gemma 4
via Ollama
   |
   v
Resume Evidence Extraction
   |
   v
Requirement Mapping
   |
   v
Safe Resume Suggestions
```

## Antigravity Command

```text
Continue from Agentic Career Lab on main.

IMPLEMENT MILESTONE 3 ONLY.

Do NOT implement:
- Skill Builder
- Google ADK coordinator
- hybrid model router
- Cloud Run
- observability

Goal:
Create a private Resume Agent using Gemma 4 running locally through Ollama.

Default:
OLLAMA_BASE_URL=http://localhost:11434
GEMMA_MODEL=gemma4:12b

Create a reusable local model abstraction.

Conceptually:

class LocalLLM(Protocol):
    async def generate(...):
        ...

class OllamaGemmaClient(LocalLLM):
    ...

Do not scatter Ollama HTTP calls throughout the codebase.

Implement:
- Ollama connectivity check
- model availability check
- helpful local error messages

Resume Agent should support:
- pasted resume text
- extracting skills
- extracting projects
- extracting experience
- extracting education
- extracting technologies
- mapping job requirements to resume evidence
- identifying missing evidence
- suggesting improved bullets
- structured Pydantic output

Critical rule:

NEVER fabricate:
- employers
- projects
- certifications
- education
- titles
- technologies
- skills
- metrics
- achievements
- responsibilities

For each resume suggestion preserve:
- original_text
- suggested_text
- evidence_used
- unsupported_claims_detected

Add deterministic validation after model generation.

If a suggestion introduces unsupported factual content:
- flag it
- reject it
- do not silently accept it

Privacy rule:

Raw resume content must stay in the local Resume Agent path.

Do not send raw resume text to Gemini or Vertex AI.

Update UI:

Private Resume Lab

Local AI Processing
Gemma 4 via Ollama

Show:
- extracted skills
- projects
- experience
- requirement-to-evidence mapping
- missing evidence

Example:

Python        -> Backend project
Docker        -> Deployment project
Vertex AI     -> No evidence found

Add side-by-side suggestion view:

CURRENT
...

SUGGESTED
...

Evidence used:
...

Safety:
- No unsupported skill added
- No fabricated achievement
- No invented metric

Document setup:

ollama pull gemma4:12b
ollama serve

Allow:
ollama run gemma4:12b

Unit tests must use a fake LocalLLM.

Do not require Ollama for unit tests.

Add an optional integration test for real Ollama.

Run:
ruff check .
ruff format --check .
pytest

Recommended commit:
feat: add private Gemma 4 resume analysis via Ollama

STOP AFTER MILESTONE 3.
```

## Verification
```bash
ollama list
ruff check .
ruff format --check .
pytest
streamlit run src/agentic_career_lab/app.py
```

## Expected Result
- local Gemma 4 resume analysis works
- resume data stays local
- evidence mapping works
- unsupported claims are rejected

## Commit
feat: add private Gemma 4 resume analysis via Ollama

## Status
Planned
