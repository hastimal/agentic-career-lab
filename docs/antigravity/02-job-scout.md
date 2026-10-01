# Milestone 2 — Job Scout Agent
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Add evidence-backed internship and job discovery with structured requirements and explainable student-to-opportunity matching.

## Goal
Add evidence-backed internship and job discovery with structured requirements and explainable student-to-opportunity matching.

## What This Milestone Adds
- Job Scout service/agent
- opportunity provider abstraction
- deterministic mock provider
- job requirement extraction
- source preservation
- skill normalization
- explainable matching
- opportunity UI

## What This Milestone Does NOT Add
- Gemma 4 resume analysis
- Ollama integration
- Skill Builder
- Google ADK orchestration
- hybrid routing
- Cloud Run deployment
- observability

## Architecture
```text
Student Profile
      |
      v
Job Scout
      |
      v
Opportunity Provider
      |
      v
Requirement Extractor
      |
      v
Skill Normalizer
      |
      v
Deterministic Matcher
      |
      v
Evidence-Backed Results
```

## Antigravity Command

```text
Continue from the current Agentic Career Lab repository.

Repository:
agentic-career-lab

Python package:
agentic_career_lab

Use main directly.

IMPLEMENT MILESTONE 2 ONLY.

Do NOT implement:
- Gemma 4 resume processing
- Ollama integration
- Skill Builder
- Google ADK coordinator
- hybrid routing
- Cloud Run deployment
- observability

Goal:
Build an evidence-backed Job Scout Agent.

The Job Scout must:
1. accept a StudentProfile
2. search opportunities through a provider abstraction
3. normalize job data
4. extract structured requirements
5. preserve source URLs
6. compare job requirements to student skills
7. produce explainable matching
8. never invent job postings

Create an OpportunityProvider abstraction.

Conceptually:

class OpportunityProvider(Protocol):
    async def search(
        self,
        query: OpportunitySearchQuery
    ) -> list[Opportunity]:
        ...

Implement:
- MockOpportunityProvider
- external provider boundary/interface

Mock provider must return clearly synthetic demo jobs.

Use example.com URLs only for synthetic data.

Create/extend models:
- OpportunitySearchQuery
- Opportunity
- OpportunityRequirement
- RequirementType
- OpportunityMatch

RequirementType:
- required
- preferred
- unknown

OpportunityMatch should include:
- demonstrated_skills
- partial_skills
- missing_skills
- why_relevant

Do not use arbitrary percentages.

Implement requirement extraction.

Example:

Input:
Candidates should have Python, Docker, and Google Cloud.
Kubernetes is preferred.

Output:
Required:
- Python
- Docker
- Google Cloud

Preferred:
- Kubernetes

Use deterministic parsing where practical.

Create an optional Gemini/Vertex AI extraction boundary for semantic cases.

Unit tests must not require live Gemini.

Implement skill normalization:
- GCP -> Google Cloud
- Google Cloud Platform -> Google Cloud
- k8s -> Kubernetes
- Postgres -> PostgreSQL

Keep normalization small and explicit.

Implement deterministic matching:
- Demonstrated
- Partial
- Missing

Do not let an LLM determine exact matches when Python can do it.

Create concise evidence-based relevance explanations.

Never say:
- guaranteed match
- guaranteed interview
- highly qualified
unless directly supported.

Update Opportunities UI.

Show:
- title
- company
- location
- source
- demonstrated evidence
- partial evidence
- missing evidence
- why relevant
- View Source
- Prepare Me

Mock results must display:
DEMO DATA

Prepare Me should only select/store the role for future milestones.

Do NOT implement Skill Builder yet.

Add minimal chat integration if useful.

No ADK orchestration yet.

Tests must cover:
- deterministic mock provider
- source URL validation
- requirement extraction
- aliases
- demonstrated match
- partial match
- missing skills
- no invented skills
- no invented requirements
- offline/no-Vertex mode
- invalid external result without source URL rejection

Run:
ruff check .
ruff format --check .
pytest

Update README with Milestone 2.

Recommended commit:
feat: add evidence-backed job scout agent

STOP AFTER MILESTONE 2.
```

## Verification
```bash
ruff check .
ruff format --check .
pytest
streamlit run src/agentic_career_lab/app.py
```

## Expected Result
- Job Scout works with demo provider
- opportunity cards render
- matching is explainable
- source URLs are preserved

## Commit
feat: add evidence-backed job scout agent

## Status
Planned
