# Docker Compose Deployment: Application + OpenTelemetry + Grafana

This guide details how to run **Agentic Career Lab** using Docker Compose with the full observability stack (**OpenTelemetry Collector**, **Prometheus**, **Tempo**, and **Grafana**).

---

## 🌟 1. Overview

While [`uvx` mode](https://github.com/hastimal/agentic-career-lab/blob/main/docs/installation/uvx.md) offers zero-clone standalone execution, **Docker Compose mode** is designed for developers, evaluators, and system architects who require:
- Containerized packaging with reproducible builds.
- Complete distributed tracing of multi-agent workflows (Job Scout, Resume Agent, Skill Builder).
- Local Ollama inference latency monitoring and span metrics.
- Pre-provisioned Grafana dashboards without manual configuration.

---

## 📋 2. Prerequisites

Before starting, ensure you have:
1. **Docker Desktop** (macOS/Windows) or **Docker Engine with Docker Compose v2+** (Linux).
2. **Local [Ollama](https://ollama.com)** installed on your host machine.
3. The **`gemma4:12b`** model pulled in Ollama (`ollama pull gemma4:12b`).
4. At least **16 GB RAM** and **15 GB free disk space** for containers, models, and traces.

---

## 💻 3. Supported Operating Systems

| OS | Container Engine | Host Ollama Connectivity | Status |
| :--- | :--- | :--- | :---: |
| **macOS (Apple Silicon)** | Docker Desktop | `host.docker.internal:11434` (Preserves native Metal GPU) | **Verified** |
| **macOS (Intel)** | Docker Desktop | `host.docker.internal:11434` (CPU inference) | **Verified** |
| **Linux (Ubuntu / Debian / RHEL)** | Docker Engine + Compose plugin | `host.docker.internal:11434` via `extra_hosts` | **Verified** |
| **Windows 10/11** | Docker Desktop (WSL2 backend) | `host.docker.internal:11434` (Native Windows Ollama) | **Verified** |

---

## 📦 4. Repository Checkout

Clone the official repository and enter the directory:

```bash
git clone https://github.com/hastimal/agentic-career-lab.git
cd agentic-career-lab
```

---

## 🦙 5. Ollama Installation and Model Preparation

Agentic Career Lab executes private resume evaluation and mentor guidance using local Gemma 4 (`gemma4:12b`):

```bash
# 1. Pull the model (approx. 8 GB download)
ollama pull gemma4:12b

# 2. Verify model availability
ollama list
```

---

## 🔄 6. Native Host Ollama vs. Containerized Ollama

The Docker Compose setup supports two Ollama topologies:

### Option A: Native Host Ollama (Recommended)
Running Ollama directly on your host machine is the **strongly recommended default**:
- **Apple Silicon macOS:** Retains 100% native Metal GPU acceleration with unified memory.
- **Windows / Linux:** Leverages native CUDA / ROCm drivers without complex container passthrough.
- **Networking:** The container reaches the host via `http://host.docker.internal:11434`.

> ⚠️ **Security Notice:** Do **never** expose Ollama publicly to `0.0.0.0` or open internet ports. Keeping it on `127.0.0.1:11434` or Docker's internal host bridge ensures privacy.

### Option B: Containerized Ollama (`standalone` Profile)
For completely self-contained Linux server deployments where Ollama cannot be installed on the host, a containerized Ollama service is provided under the `standalone` profile:
```bash
docker compose --profile standalone up -d
```
*Note: Containerized Ollama stores models in the persistent volume `agentic_career_lab_ollama_models` and defaults to CPU inference unless GPU passthrough is explicitly configured.*

---

## 🏗️ 7. Docker Compose Profiles

The compose configuration ([`docker-compose.yml`](https://github.com/hastimal/agentic-career-lab/blob/main/docker-compose.yml)) defines explicit service profiles:

| Profile | Included Services | Description |
| :--- | :--- | :--- |
| *(default)* | `app` | Core Streamlit application connected to host Ollama. |
| `observability` | `app`, `otel-collector`, `prometheus`, `tempo`, `grafana` | Complete multi-agent observability and telemetry stack. |
| `standalone` | `app`, `ollama` | Self-contained app with containerized Ollama. |

---

## 🚀 8. Starting Full Observability Mode

To build and start the application with the full monitoring and tracing pipeline:

```bash
docker compose --profile observability up -d --build
```

---

## 🩺 9. Verifying Container Health

Check the status of all services:
```bash
docker compose ps
```

Expected output:
```text
NAME                                IMAGE                                          STATUS
agentic-career-lab-app              agentic-career-lab:latest                      Up (healthy)
agentic-career-lab-grafana          grafana/grafana:11.2.0                         Up
agentic-career-lab-otel-collector   otel/opentelemetry-collector-contrib:0.111.0   Up
agentic-career-lab-prometheus       prom/prometheus:v2.54.1                        Up
agentic-career-lab-tempo            grafana/tempo:2.6.1                            Up
```

Test the core healthcheck endpoints:
```bash
# Application health
curl -fsS http://localhost:8501/_stcore/health

# Grafana health
curl -fsS http://localhost:3000/api/health

# Prometheus health
curl -fsS http://localhost:9090/-/healthy

# Tempo readiness
curl -fsS http://localhost:3200/ready
```

---

## 🌐 10–13. Service Access & Endpoints

| Service | Local URL | Credentials | Purpose |
| :--- | :--- | :--- | :--- |
| **Streamlit Web App** | [http://localhost:8501](http://localhost:8501) | *None* | Interactive career assistant interface |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | *Anonymous Admin (pre-configured)* | Observability dashboards & trace inspection |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | *None* | Time-series metrics and OTel scrapers |
| **Tempo API** | [http://localhost:3200](http://localhost:3200) | *None* | Distributed tracing backend |
| **OTel Collector gRPC** | `localhost:4317` | *Internal* | OpenTelemetry Protocol ingestion |

---

## 📊 14. Grafana Dashboards & Tempo Tracing

### Provisioned Dashboard
1. Open [http://localhost:3000](http://localhost:3000) in your browser.
2. Navigate to **Dashboards** $\rightarrow$ **Agentic Career Lab** $\rightarrow$ **Agentic Career Lab Observability**.
3. View real-time panels:
   - **Recent Multi-Agent Spans:** TraceQL table querying `{resource.service.name = "agentic-career-lab"}`.
   - **OTel Collector System Uptime & Scrapes:** Real-time uptime and scrape performance.

### Inspecting a Multi-Agent Trace
When a workflow action executes (e.g. Resume Analysis or Job Search), OpenTelemetry captures structured hierarchy:
```text
coordinator.prepare_resume
 ├── agent.private_resume
 │    └── llm.ollama.generate (Local Gemma 4 inference latency)
 └── agent.skill_builder
      └── tool.catalog_match (Deterministic 104-item mapping)
```

Click any Trace ID in Grafana to open the detailed Tempo timeline and inspect span duration, token streaming metrics, and agent tool execution.

---

## 🧪 15. Synthetic End-to-End Workflow & Trace Verification

To verify that telemetry flows into Tempo and Prometheus:
1. Open [http://localhost:8501](http://localhost:8501).
2. Select target role: **Cloud Engineer**.
3. Use the built-in synthetic resume sample or upload a document.
4. Click **Analyze Resume (Local Gemma 4)**.
5. In Grafana ([http://localhost:3000/explore](http://localhost:3000/explore)), select **Tempo** as data source, click **Search**, and confirm traces with root name `coordinator.prepare_resume` appear.

---

## 🔒 16. Privacy and Telemetry Security

Agentic Career Lab enforces strict privacy boundaries even in full observability mode:
- **Redacted Trace Payloads:** OpenTelemetry trace attributes **never** record raw resume text, student PII, contact info, or PDF byte strings.
- **Zero Cloud Leakage:** Local telemetry stays entirely inside your host Docker bridge network.
- **Allowlist Filtering:** If optional cloud synthesis is enabled, only high-level skill names are sent to external APIs with recorded consent.

---

## ❓ 17. Troubleshooting Guide

### 1. `app` Container Fails with `Connection refused` to Ollama
- **Cause:** Ollama is not running on the host machine or is not listening on the expected bridge IP.
- **Fix:**
  - Verify Ollama is running on host: `curl http://localhost:11434/api/tags`.
  - On Linux, ensure `host.docker.internal` resolves (Docker Compose adds `host.docker.internal:host-gateway` automatically).

### 2. Port `8501` or `3000` Already in Use
- **Cause:** A previous instance or local service occupies the port.
- **Inspection (macOS / Linux):** `lsof -i :8501` or `lsof -i :3000`.
- **Inspection (Windows PowerShell):** `Get-NetTCPConnection -LocalPort 8501 -State Listen`.
- **Fix:** Stop conflicting services or map alternate ports in `.env`.

### 3. Missing Traces in Grafana
- **Cause:** OTel Collector batch timeout is set to 1s. Ensure you have executed an action in Streamlit and wait 5 seconds before refreshing.

---

## 🔄 18. Updating Containers

To pull upstream image updates and rebuild:
```bash
git pull origin main
docker compose --profile observability up -d --build
```

---

## 🛑 19–20. Stopping & Safe Cleanup

### Stop Services (Preserving Data):
```bash
docker compose --profile observability stop
```

### Shut Down Containers and Networks:
```bash
docker compose --profile observability down
```

### Irreversible Volume Removal (Caution):
> ⚠️ **Warning:** The following command deletes all local Prometheus metrics, Tempo traces, and containerized Ollama models.
```bash
docker compose --profile observability down -v
```
