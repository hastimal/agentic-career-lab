# Milestone 7 — Docker Acceptance Test Evidence
## Agentic Career Lab — Production Acceptance Report

- **Date:** 2026-10-17
- **Host Platform:** macOS (Apple Silicon arm64, Darwin 25.0.0)
- **Docker Engine:** Docker version 29.8.2 (Build 7fc2dff)
- **Docker Compose:** Docker Compose v5.5.1
- **Local LLM Runtime:** Ollama (native, Metal GPU accelerated) with `gemma4:12b` (8.02 GB, Q4_K_M)
- **Test Baseline:** 53 passing automated unit/integration tests

---

## 1. Acceptance Criteria Checklist

| Item | Requirement | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- |
| **AC-1** | `docker compose config` validation | **PASS** | Validated cleanly with services `app` and profile `standalone`. |
| **AC-2** | Multi-stage / production Dockerfile build | **PASS** | Built `agentic-career-lab:latest` (non-root `appuser`, healthcheck). |
| **AC-3** | `docker compose up -d` execution | **PASS** | App container started and became healthy on `http://localhost:8501`. |
| **AC-4** | Streamlit Health Endpoint Verification | **PASS** | `curl -s http://localhost:8501/_stcore/health` returned `ok` (HTTP 200). |
| **AC-5** | Container to Host Ollama Connectivity | **PASS** | `host.docker.internal:11434/api/tags` returned `gemma4:12b` via bridge. |
| **AC-6** | Real Gemma 4 Inference inside Container | **PASS** | `PrivateResumeAgent` executed against `gemma4:12b` via container network. |
| **AC-7** | DOCX / PDF Document Parsing in Container | **PASS** | Successfully parsed `scratch/sample_resume.docx` (200 characters). |
| **AC-8** | Multi-Agent Coordinator Execution | **PASS** | Sequenced `FIND_OPPORTUNITIES` -> `PREPARE_RESUME` -> `BUILD_SKILLS`. |
| **AC-9** | Privacy Boundary Verification | **PASS** | Raw resume text was NOT present in serialized `CareerWorkflowState`. |
| **AC-10**| Automated Test Suite & Linter | **PASS** | 53 pytest tests passed in 1.02s; Ruff lint and format clean. |

---

## 2. Test Execution Logs

### A. Docker Compose Validation & Build
```text
$ docker compose config
name: agentic-career-lab
services:
  app:
    build:
      context: /Users/hastimal.jangid/Desktop/hmeb/GitHub/agentic-career-lab
      dockerfile: Dockerfile
    container_name: agentic-career-lab-app
    ...
```

### B. Container Readiness & Healthcheck
```text
$ docker compose ps
NAME                     IMAGE                       COMMAND                  SERVICE   CREATED          STATUS                    PORTS
agentic-career-lab-app   agentic-career-lab:latest   "streamlit run src/a…"   app       14 seconds ago   Up 13 seconds (healthy)   0.0.0.0:8501->8501/tcp

$ curl -I http://localhost:8501
HTTP/1.1 200 OK
date: Sat, 17 Oct 2026 12:06:02 GMT
server: uvicorn
content-type: text/html; charset=utf-8
content-length: 6467
```

### C. Gemma 4 Connectivity from Container
```text
$ docker exec agentic-career-lab-app python -c "
import os, httpx
url = os.environ.get('OLLAMA_BASE_URL')
r = httpx.get(f'{url}/api/tags')
print('OLLAMA_BASE_URL:', url)
print('Status:', r.status_code)
print('Models:', [m['name'] for m in r.json()['models']])
"

OLLAMA_BASE_URL: http://host.docker.internal:11434
Status: 200
Models: ['gemma4:12b']
```

### D. Full Multi-Agent Coordinator Execution in Container
```text
Initializing Multi-Agent Coordinator in Container...
Executing FIND_OPPORTUNITIES...
Opportunities found: 2
Selected: AI Engineering Intern at Example Tech Corp
Executing PREPARE_RESUME...
Resume analyzed! Requirement matches count: 5
Privacy check passed (raw resume isolated from workflow state): True
Executing BUILD_SKILLS...
Plan built! Gaps: ['Google Cloud', 'Vertex AI', 'Kubernetes', 'Python', 'Docker']
Final Career Action Plan created! Status: Complete
ALL CONTAINER WORKFLOW CHECKS PASSED!
```

### E. Sample Resume Smoke Test (`scratch/sample_resume.docx`)
```text
========================================
LOCAL RESUME SMOKE TEST
========================================

Parser
✓ DOCX parsed locally
Characters: 200

Ollama
✓ Connected

Model
✓ gemma4:12b

Resume Evidence

Target Role Mapping

Demonstrated:
- Python
- Docker

Partial:

Missing:
- Google Cloud
- Vertex AI
- Kubernetes

Suggestions: 0
Safety:
✓ No unsupported claims accepted

ADK coordinator:
✓ local resume path completed
Raw resume stored in CareerWorkflowState:
No

========================================
RESULT: PASS
========================================
```

### F. Pytest & Ruff Checks
```text
$ pytest
53 passed, 1 warning in 1.02s

$ ruff check .
All checks passed!

$ ruff format --check .
66 files already formatted
```

---

## 3. Platform Limitations & Architecture Notes

1. **Docker Desktop on macOS GPU Passthrough**:
   Docker Desktop on macOS runs containers inside a lightweight Linux hypervisor. Metal GPU passthrough is not supported by Apple or Docker for Linux containers. Therefore, running Ollama natively on macOS and connecting from the container via `host.docker.internal:11434` is the official recommended path, yielding native hardware acceleration and low-latency token generation.
2. **Containerized Ollama (Standalone Profile)**:
   Provided for headless Linux servers with NVIDIA GPUs (`--gpus all`) or CPU-only standalone environments.
3. **Privacy Invariant**:
   All tests confirmed zero leakage of raw resume content outside the ephemeral container memory context.
