# Agentic Career Lab — Build Runbooks
## Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

These runbooks contain the reproducible Antigravity prompts used to incrementally build Agentic Career Lab.

The repository is intentionally built milestone-by-milestone so developers can understand and reproduce the architecture instead of only seeing the final code.

                           Student
                              |
                              v
                    Career Coordinator
                       Google ADK
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
     Job Scout         Private Resume        Skill Builder
       Agent               Agent                Agent
          |                   |                   |
          v                   v                   v
 Gemini / Vertex AI     Gemma 4 Local       Gemini / Python
                            Ollama
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                       Career Action Plan

## Model Strategy

Fresh/current information
-> Gemini + Vertex AI

Agent orchestration
-> Google ADK

Private resume processing
-> Gemma 4 running locally through Ollama

Deterministic matching
-> Python

Deployment
-> Docker + Cloud Run

Production insight
-> Evaluation + OpenTelemetry

## Milestones

| # | Milestone | Primary Technology | Status |
|---|---|---|---|
| 1 | [Foundation](01-foundation.md) | Python + Streamlit | Complete |
| 2 | [Job Scout](02-job-scout.md) | Gemini + Vertex AI | Planned |
| 3 | [Private Resume Agent](03-private-gemma4-ollama-resume.md) | Gemma 4 + Ollama | Planned |
| 4 | [Skill Builder](04-skill-builder.md) | Gemini + Python | Planned |
| 5 | [Multi-Agent Coordinator](05-google-adk-coordinator.md) | Google ADK | Planned |
| 6 | [Hybrid Routing](06-hybrid-gemini-gemma4-routing.md) | Gemini + Gemma 4 | Planned |
| 7 | [Cloud Deployment](07-cloud-run-deployment.md) | Docker + Cloud Run | Planned |
| 8 | [Evaluation + Observability](08-evaluation-observability.md) | OpenTelemetry | Planned |

## Core Principles

- Do not fabricate jobs.
- Do not fabricate resume content.
- Keep raw resume data local by default.
- Use deterministic Python when LLM reasoning is unnecessary.
- Preserve evidence and sources.
- Prefer explainable matching over arbitrary scores.
- Keep the architecture teachable.
- Build milestone-by-milestone.
