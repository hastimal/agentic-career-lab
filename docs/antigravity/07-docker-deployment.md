# Milestone 7 — Docker-First Application Distribution
## Agentic Career Lab — Reproducible Docker Deployment Architecture

> Reproducible local and containerized multi-agent career workspace distribution with Docker Compose, preserving native Gemma 4 Metal GPU acceleration on macOS and strict privacy boundaries.

---

## 1. Executive Summary

Milestone 7 delivers a production-conscious, reproducible Docker packaging and distribution layer for the Agentic Career Lab v0.6.0 hybrid AI career platform.

### Core Objectives Achieved
1. **Zero-Configuration Startup**: Single command startup (`docker compose up -d`) mapping the Streamlit UI to `http://localhost:8501`.
2. **Containerized Streamlit Application**: Multi-stage/production-ready Dockerfile based on `python:3.11-slim` running as a non-root `appuser` (UID 1000) with integrated container healthchecks (`curl -fsS http://localhost:8501/_stcore/health`).
3. **Hardware-Aware Ollama Architecture**:
   - **Default Native Mode (macOS / Apple Silicon / Developers)**: Routes traffic through `host.docker.internal:11434` with host gateway mapping. This preserves full Apple Silicon Metal GPU acceleration and instant inference speeds (Docker Desktop on macOS cannot pass Metal GPUs to Linux containers).
   - **Standalone Profile Mode (Linux Servers / Self-Contained)**: Docker Compose profile (`--profile standalone`) orchestrating an isolated `ollama/ollama:latest` container with a named persistent Docker volume (`agentic_career_lab_ollama_models`).
4. **Air-Gapped Privacy Boundary**: Local resume data, parsing (`pypdf`, `python-docx`), and inference (`gemma4:12b`) execute strictly against the local Ollama instance and are never logged or transmitted externally.

---

## 2. Docker Architecture

![Docker Architecture](../images/docker-architecture.svg)

### Service Topology

```text
Host System (macOS Apple Silicon / Linux / Windows)
 ├── Port 8501: Ingress to Streamlit Web Application
 └── Port 11434: Native Ollama Runtime (Metal GPU accelerated)
       │
       ▼ (host.docker.internal)
Docker Compose Network (agentic-career-lab_default)
 ├── Container: agentic-career-lab-app
 │     ├── Base: python:3.11-slim
 │     ├── User: appuser (UID 1000, non-root)
 │     ├── Healthcheck: GET /_stcore/health (every 10s)
 │     ├── Google ADK Multi-Agent Coordinator
 │     ├── Private Resume Agent (Gemma 4 via Ollama client)
 │     ├── Job Scout Agent (Mock / Adzuna)
 │     └── Skill Builder Agent (Deterministic / Hybrid Gemini)
 └── (Optional Profile: standalone)
       └── Container: agentic-career-lab-ollama
             ├── Base: ollama/ollama:latest
             ├── Volume: agentic_career_lab_ollama_models -> /root/.ollama
             └── Bind: 127.0.0.1:11434 (Loopback only)
```

---

## 3. Configuration & Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Target endpoint for local Gemma 4 Ollama instance. |
| `GEMMA_MODEL` | `gemma4:12b` | Model tag for private local resume inference. |
| `JOB_PROVIDER` | `mock` | Opportunity search provider (`mock` or `adzuna`). |
| `ADZUNA_APP_ID` | `""` | Optional Adzuna Application ID for live jobs. |
| `ADZUNA_APP_KEY` | `""` | Optional Adzuna Application Key. |
| `ADZUNA_COUNTRY` | `us` | Country code for Adzuna job queries. |
| `GOOGLE_CLOUD_PROJECT` | `""` | Optional GCP Project ID for Gemini reasoning. |
| `GOOGLE_CLOUD_LOCATION`| `us-central1` | GCP region for Vertex AI endpoints. |
| `GEMINI_API_KEY` | `""` | Optional Gemini API Key for hybrid skill planning. |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model version for cloud planning. |

---

## 4. Operational Instructions

### Mode A: Recommended for macOS & Apple Silicon (Native Ollama)
```bash
# 1. Start Ollama natively on host (if not already running)
ollama run gemma4:12b

# 2. Build and launch container
docker compose up -d

# 3. Check health and logs
docker compose ps
docker compose logs -f app
```

### Mode B: Standalone Linux / Server Deployment (Containerized Ollama)
```bash
# 1. Launch both app and containerized Ollama
docker compose --profile standalone up -d

# 2. Pull Gemma 4 into persistent container volume
docker exec -it agentic-career-lab-ollama ollama pull gemma4:12b
```

---

## 5. Security & Privacy Posture

1. **Non-Root Execution**: Container runs under unprivileged `appuser` (UID 1000).
2. **Loopback Ollama Binding**: Ollama is bound to `127.0.0.1:11434` on the host, preventing external network exposure.
3. **No Secrets in Images**: `.dockerignore` excludes `.env`, secrets, `.venv`, and caches from build layers.
4. **Isolated Raw State**: Raw resume text is held purely in memory within `LocalResumeContext` during inference and excluded from persistent `CareerWorkflowState`.
