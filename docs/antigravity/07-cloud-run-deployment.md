# Milestone 7 — Docker + Google Cloud Run Deployment
## Agentic Career Lab — Gemini + Gemma 4 on Ollama + Google ADK + Vertex AI

> Containerize and deploy the cloud-capable portion of Agentic Career Lab while preserving the local Gemma 4 privacy boundary.

## Goal
Containerize and deploy the cloud-capable portion of Agentic Career Lab while preserving the local Gemma 4 privacy boundary.

## What This Milestone Adds
- Docker image
- Cloud Run startup path
- health/readiness behavior
- Vertex AI authentication using service identity / ADC
- deployment shell script
- local-vs-cloud mode documentation

## What This Milestone Does NOT Add
- Secret Manager
- CI/CD
- GKE
- Terraform
- cloud-hosted Ollama
- fake localhost-to-Cloud-Run connectivity

## Architecture
```text
LOCAL FULL MODE

Streamlit
   |
   v
Google ADK
   +--> Gemini / Vertex AI
   +--> Gemma 4 / Ollama

CLOUD MODE

Cloud Run
   |
   v
Google ADK
   |
   v
Gemini / Vertex AI

Private Resume:
Local Private Mode required
```

## Antigravity Command

```text
Continue from Agentic Career Lab on main.

IMPLEMENT MILESTONE 7 ONLY.

Goal:
Dockerize and deploy the cloud-capable application to Google Cloud Run.

Do NOT add:
- Secret Manager
- CI/CD
- GKE
- Terraform

Implement:
- Dockerfile
- .dockerignore
- Cloud Run-compatible startup
- port configuration
- health endpoint or equivalent health check
- Google Cloud project/location config
- Vertex AI authentication using service identity / Application Default Credentials
- deployment shell script
- Cloud Run documentation

Environment configuration should include:
- PROJECT_ID
- REGION
- SERVICE_NAME
- GOOGLE_CLOUD_LOCATION
- GEMINI_MODEL

Do not hard-code credentials.

Important:

Cloud Run cannot access a user's localhost Ollama service.

Therefore document two modes.

LOCAL FULL MODE:

Streamlit
-> Google ADK
-> Gemini / Vertex AI
-> Gemma 4 / local Ollama

All features available.

CLOUD MODE:

Cloud Run
-> Google ADK
-> Gemini / Vertex AI

Private Resume Agent:
requires local mode

UI must clearly show:
Private Resume Analysis — Available in Local Private Mode

Do not pretend Cloud Run can call localhost Ollama.

Create:
scripts/deploy_cloud_run.sh

Make configurable:
PROJECT_ID
REGION
SERVICE_NAME

Test Docker locally if Docker is available.

Run:
ruff check .
ruff format --check .
pytest

Recommended commit:
feat: add Docker and Cloud Run deployment

STOP AFTER MILESTONE 7.
```

## Verification
```bash
ruff check .
ruff format --check .
pytest
docker build -t agentic-career-lab .
```

## Expected Result
- local full mode works
- cloud mode works
- Gemini/Vertex AI works in Cloud Run
- local Gemma 4 boundary is clear
- no false claim that Cloud Run can reach local Ollama

## Commit
feat: add Docker and Cloud Run deployment

## Status
Planned
