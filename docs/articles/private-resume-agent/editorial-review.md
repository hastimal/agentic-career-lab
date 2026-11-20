# Editorial, Technical Accuracy, and Security Audit Review

**Article**: `docs/articles/private-resume-agent/article.md`  
**Publishing Package**: `docs/articles/private-resume-agent/medium-package.md`  
**Auditor**: Senior AI Architect & Cloud-Native Reviewer  
**Status**: Completed & Verified  

---

## 1. Executive Summary

This audit rigorously inspected the implementation, trace logs, telemetry exports, Docker topologies, unit tests, and security boundaries of [Agentic Career Lab](https://github.com/hastimal/agentic-career-lab). 

The goal was to transition the article from marketing-oriented phrasing to an authoritative, publication-ready engineering story suitable for the **Google Cloud Community**, **Medium**, or a **Google Developer Expert (GDE)** technical portfolio.

---

## 2. Technical Claims Verified Against Source Code

| Feature / Claim | Original Claim in Draft | Audit Finding & Verification | Revised Action / Text in Article |
| :--- | :--- | :--- | :--- |
| **Gemma 4 Local Model** | Gemma 4 12B local inference | ✅ Verified in [`src/agentic_career_lab/llm/local.py`](../../src/agentic_career_lab/llm/local.py#L18). Default `model_name="gemma4:12b"` calls Ollama REST endpoint `/api/generate`. | Accurately explained parameters, local Ollama CLI commands, and defensive timeout handling (`OLLAMA_TIMEOUT=180s`). |
| **Google ADK Orchestration** | Implied ADK runner executes live runtime loops | ⚠️ **Nuance Verified**: The project uses custom Python coordinator logic in `CareerCoordinator`. `ADKCareerCoordinator` acts as an architectural facade over deterministic tools. | Clarified that the execution engine uses custom sequential dispatch to eliminate agentic reasoning overhead for predictable workflows. |
| **Trace Hierarchy & Timings** | Single 98-second inference span | ❌ **Inaccurate in previous draft**: Real trace `947c2209b3513394471ff14a0675c9ec` shows a **four-span waterfall** with **two distinct Ollama calls** (40.4s and 60.6s). | Replaced the 1-call narrative with the verified 2-call waterfall breakdown: extraction call + rewrite/suggestion call totaling ~101.0s. |
| **Grafana Dashboard** | Included screenshot of Grafana dashboard | ❌ **Defect in previous image**: The captured dashboard showed `Unauthorized` and an empty spans panel. | **Omitted unverified screenshot** in compliance with editorial requirements. Replaced with authentic Tempo trace waterfall and programmatic architecture diagrams. |
| **Docker Python Runtime** | Containerized Streamlit UI | ✅ Verified in [`Dockerfile`](../../Dockerfile#L2). Uses `python:3.11-slim`, unprivileged `appuser` (UID `10001`), and healthcheck. | Code listing streamlined to essential configuration. |
| **Docker Networking** | Bridges to native Ollama | ✅ Verified in [`docker-compose.yml`](../../docker-compose.yml#L13). Uses `extra_hosts: ["host.docker.internal:host-gateway"]` to connect container to host port `11434`. | Retained and emphasized Apple Silicon Metal acceleration benefits. |

---

## 3. Unverified Marketing Claims Removed

The following terms were audited and systematically excised from the article:
- ❌ *"Zero resume leakage"* → Replaced with: *"Implemented architectural boundaries that isolate raw resume text from cloud payloads."*
- ❌ *"Enterprise-grade"* → Replaced with: *"Production-aligned architecture with non-root Docker images and OpenTelemetry tracing."*
- ❌ *"Complete privacy guarantee"* → Replaced with: *"Architectural privacy controls with known operational limitations."*
- ❌ *"Guaranteed memory-only processing"* → Replaced with: *"In-memory parsing during session lifecycle with explicit limitations regarding operating system swap, core dumps, and debug logging."*
- ❌ *"Fixed 35–60 tokens/second"* → Replaced with observed benchmark ranges and latency measurements without unsupported throughput guarantees.
- ❌ *"100% PII-free observability"* → Replaced with detailed findings on attribute filtering and exception-handling attack vectors.

---

## 4. Security & Privacy Audit Findings

### Audit Investigation: OpenTelemetry Exception Handling

We audited [`src/agentic_career_lab/observability.py`](../../src/agentic_career_lab/observability.py#L160-L175) to evaluate how exceptions are recorded in OpenTelemetry spans:

```python
with tracer.start_as_current_span(name, attributes=attrs) as span:
    try:
        yield span
    except Exception as exc:
        span.set_attribute("error.type", type(exc).__name__)
        span.set_attribute("error.message", str(exc)[:200])  # Truncate error message safely
        span.record_exception(exc)
        span.set_status(Status(StatusCode.ERROR, str(exc)))
        raise
```

### Critical Findings:

1. **Span Attributes Sanitization**:
   - The sanitizer strips keys containing `"resume"`, `"prompt"`, `"response"`, `"pii"`, or `"content"` from custom attributes.
   - ✅ Custom metadata passed in `attributes={}` is sanitized.
2. **Exception Object Leak Vector (`span.record_exception(exc)`)**:
   - When an unhandled exception occurs (e.g., inside JSON parsing, downstream network libraries, or validation logic), Python's exception message (`str(exc)`) or traceback may embed prompt text or candidate details.
   - `span.record_exception(exc)` serializes the full Python stacktrace into an OpenTelemetry Span Event (`exception.stacktrace`).
   - `span.set_status(Status(StatusCode.ERROR, str(exc)))` records the raw exception string in the span status description.
   - ⚠️ **Key Finding**: Attribute filtering alone does **not** protect against leaks inside exception stacktraces or error messages.

### Proposed Production Remediation (For Future Minor Version):
In a future release, `trace_span` should sanitize `str(exc)` before calling `span.set_status()` and avoid recording raw stacktraces containing local variable values if they could contain candidate PII. This finding is documented in the article under **Engineering Lessons & Limitations**.

---

## 5. Visual Assets Improvements

| Asset Name | Status | Changes Made |
| :--- | :---: | :--- |
| **`cover-art-architecture.png`** | ✅ Accepted | High-resolution 16:9 isometric illustration showcasing the stack components. |
| **`diagram-a-private-resume-architecture.png`** | ✅ New Clean Asset | 16:9 horizontal vector-rendered diagram showing student upload → in-memory parser → Streamlit UI → Private Resume Agent → Docker boundary (`host.docker.internal`) → Native Ollama with Apple Silicon Metal acceleration → Gemma 4. |
| **`diagram-b-privacy-observability.png`** | ✅ New Clean Asset | 16:9 horizontal vector-rendered diagram separating sanitized telemetry (OTel Collector → Tempo / Prometheus / Grafana) from optional consent-gated cloud reasoning (Gemini Flash). |
| **`ui-my-resume.png`** | ✅ Verified | Authentic Streamlit UI capture showing uploaded resume status, privacy notice, and local Gemma 4 evidence extraction triggers. |
| **`tempo-trace-waterfall.png`** | ✅ Cropped & Verified | Cropped to focus on the authentic 4-span waterfall hierarchy (`coordinator.prepare_resume` → `agent.private_resume` → 2× `llm.ollama.generate`), removing unneeded browser margins. |
| **`grafana-dashboard.png`** | ❌ Omitted | Omitted due to "Unauthorized" error in original screenshot. Replaced by authentic Tempo trace waterfall and clean architecture diagrams. |

---

## 6. Code Excerpts Verification

Every code snippet in the revised article has been checked against the repository:

1. **`src/agentic_career_lab/llm/local.py`**:
   - Excerpt verified from lines 42–78.
   - Accurately demonstrates OTel span context manager and timeout handling without claiming false token-per-second values.
2. **`src/agentic_career_lab/agents/resume_agent/agent.py`**:
   - Excerpt verified from lines 22–75.
   - Demonstrates hard architectural assertion: fail-closed if Ollama is unreachable, with zero silent fallback to cloud models.
3. **`src/agentic_career_lab/observability.py`**:
   - Excerpt verified from lines 135–175.
   - Accurately demonstrates attribute key denylist filtering and latency measurement.

---

## 7. Verification Test Runs

- **Full Pytest Suite**:
  - `113 passed, 1 warning in 1.76s`
- **Routing and Privacy Tests**:
  - `tests/test_routing.py` and `tests/test_evaluation_observability.py`: 13 passed in 0.57s.
- **Git Tree Status**:
  - `git diff --check`: Clean, zero trailing whitespace or formatting defects.

