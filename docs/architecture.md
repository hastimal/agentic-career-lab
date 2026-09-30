# OpenCareer Agents Architecture

## Overview

OpenCareer Agents is a privacy-aware hybrid multi-agent career platform designed specifically for college students seeking internships and early-career roles.

```text
Student
   ↓
Career Coordinator — Google ADK
   │
   ├── Job Scout Agent
   │      └── Gemini / Vertex AI + Job Search Tools
   │
   ├── Private Resume Agent
   │      └── Gemma 4 via local Ollama (Privacy Boundary)
   │
   └── Skill Builder Agent
          └── Gemini / Deterministic Python
```

## Architectural Principles

1. **Privacy-First Resume Processing**:
   - Resumes contain personally identifiable information (PII) and student history.
   - All resume parsing, evidence extraction, and bullet point improvement occur **locally** via Gemma 4 running on Ollama (`http://localhost:11434`).
   - Raw resume text is **never** sent to cloud models.

2. **Evidence-Grounded Opportunity Intelligence**:
   - Job Scout uses Gemini on Vertex AI to extract explicit requirements from verifiable external opportunity sources.
   - Fabricated opportunities or missing source links are strictly rejected.

3. **Deterministic Business Logic**:
   - Matching requirements to extracted evidence is performed with deterministic Python comparison.
   - LLMs explain reasoning and synthesize learning roadmaps, rather than hallucinating arbitrary percentage match scores (e.g. 87% vs 92%).

4. **8-Milestone Incremental Delivery**:
   - Milestone 1: Foundation + Modern UI Shell
   - Milestone 2: Evidence-Backed Job Scout Agent
   - Milestone 3: Private Resume Agent with Gemma 4 + Ollama
   - Milestone 4: Opportunity-Driven Skill Builder Agent
   - Milestone 5: Google ADK Multi-Agent Coordinator
   - Milestone 6: Hybrid Gemini + Gemma Privacy Routing
   - Milestone 7: Docker + Cloud Run Deployment
   - Milestone 8: Evaluation & Observability
