# Milestone 6 Working Demo Audit Report
**Repository**: `agentic-career-lab`  
**Milestone**: M6 — Hybrid Gemini + Gemma Privacy Routing Working Demo  
**Date**: October 11, 2026  
**Status**: Completed & Verified  

---

## 1. Implemented Functionality Audit

### A. Privacy-Preserving Resume Analysis (Local Gemma 4 via Ollama)
- **Local Model**: `gemma4:12b` executed via Ollama (`http://localhost:11434/api/generate`).
- **Hard Privacy Boundary**: Raw resume text is processed strictly on local hardware. Cloud fallback is explicitly forbidden (`cloud_allowed=False`, `fallback_allowed=False`).
- **Schema & Extraction**: Correctly parses raw text, extracts skills (`Python`, `Docker`, `SQL`, `FastAPI`), identifies education and projects, and maps against target role requirements.
- **Claim Validation**: Deterministic validator (`ClaimValidator`) cross-checks suggestions against extracted evidence, flagging unverified metrics or fabricated technologies with 0 unsupported claims allowed.

### B. Cloud Opportunity & Planning Reasoning (Gemini Flash on Vertex AI / Gemini API)
- **Cloud Models**: `gemini-3.6-flash` and `gemini-3.8-flash` via Google GenAI SDK.
- **Resilient Fallback**: Gracefully detects local environment configuration (API key vs. Vertex AI project) and falls back to deterministic Python if cloud credentials are absent or if explicit user consent is withheld.
- **Cloud Planning Context**: Strips all PII and raw resume content, transmitting only sanitized target role metadata and skill gap names (`target_role`, `required_skills`, `demonstrated_skills`, `missing_skills`).
- **Privacy Guard Enforcement**: `assert_cloud_safe()` strictly blocks forbidden keys (`raw_resume_text`, `email`, `phone`, `address`, `full_resume`) and checks against any leaked secret markers.

### C. Multi-Agent Orchestration (Google ADK)
- **Coordinator**: `ADKCareerCoordinator` acts as a facade over domain coordinator `CareerCoordinator`, registering `job_scout`, `private_resume_agent`, and `skill_builder` agents.
- **State Management**: Encapsulated within `CareerWorkflowState`. Raw resume text resides strictly within transient `LocalResumeContext` and is never serialized into persistent cloud or shared workflow state.
- **Career Action Plan**: Compiles targets, evidence summaries, priority skill gaps, curated educational resources, weekly learning steps, and an actionable portfolio project into a unified `CareerActionPlan`.

### D. User Interface & Consent Flow (Streamlit)
- **Workflow Steps**:
  1. **Find Opportunities**: Search and browse internships (labeled `LIVE` from Adzuna or `DEMO DATA` from mock fixtures).
  2. **Prepare Resume**: Upload PDF/DOCX/TXT or paste text. Privately analyze with local Gemma 4.
  3. **Build Skills**: Review evidence-based gaps, explicitly grant or decline cloud sharing consent via a dedicated privacy checkbox, and generate a 2-week or 4-week learning roadmap with portfolio projects.
  4. **Final Action Plan**: Review the complete compiled career action plan.
  5. **Agent Activity**: Inspect live telemetry events, runtimes, latency, and privacy classifications.

---

## 2. Test Execution & Verification

### A. Pytest Suite
```bash
.venv/bin/pytest -v
```
- **Result**: `53 passed, 1 warning in 0.69s` (100% pass rate).
- **Coverage**: Routing policies, privacy guard assertions, opportunity providers, resume parsing, claim validation, deterministic and cloud planning fallbacks, and UI progress helpers.

### B. Lint & Formatting (Ruff)
```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```
- **Result**: `All checks passed! 64 files already formatted.`

### C. Live Gemma 4 / Ollama Smoke Test
```bash
.venv/bin/python scripts/smoke_resume_local.py scratch/sample_resume.txt
```
- **Result**: `RESULT: PASS`
- **Output Details**:
  - Model: `gemma4:12b` connected at `http://localhost:11434`
  - Extraction: `Python`, `Docker` demonstrated; `Google Cloud`, `Vertex AI`, `Kubernetes` missing
  - Safety: `✓ No unsupported claims accepted`
  - ADK Coordinator: `✓ local resume path completed`
  - Privacy Check: `Raw resume stored in CareerWorkflowState: No`

### D. End-to-End Workflow Verification
- **Job Scout**: Selected `AI Engineering Intern` (labeled `DEMO DATA`, `is_demo=True`).
- **Private Resume Agent**: Analyzed 963-character student resume locally in Ollama `gemma4:12b`.
- **Privacy Check**: `sample_resume in state.model_dump_json() == False`.
- **Skill Builder**: Synthesized 4-week learning plan and portfolio project (`Cloud-Native AI Microservice Pipeline on GKE and Vertex AI`) using Cloud Gemini in 8.0s.
- **Career Action Plan**: Produced `CareerActionPlan(workflow_status='Complete')`.

---

## 3. Discovered Issues & Resolutions

| Issue | Root Cause | Resolution |
|---|---|---|
| Smoke script import error | `FakePlanningLLM` renamed to `DeterministicPlanningLLM` in previous refactor. | Added `FakePlanningLLM = DeterministicPlanningLLM` backward-compatibility alias in `planner.py`. |
| Smoke script Pydantic validation error | `source_url` required valid `HttpUrl` but mock string `DEMO / SYNTHETIC` was passed. | Updated smoke script fixture URL to valid `https://example.com/demo-synthetic`. |
| Smoke script attribute error | Script accessed `m.requirement.skill` instead of `m.requirement` (string). | Corrected attribute access in smoke script to match `RequirementEvidenceMatch` schema. |
| Ollama generation timeout | Default 30s timeout expired during model load / heavy prompt generation. | Made `OLLAMA_TIMEOUT` configurable with a generous 120s default; warmed up local model. |
| Vertex AI client error | `GOOGLE_CLOUD_PROJECT=your-gcp-project-id` placeholder prevented falling back to `GEMINI_API_KEY`. | Added check to bypass placeholder project and fallback directly to standard `GEMINI_API_KEY` for Developer API (`gemini-3.6-flash` / `gemini-3.8-flash`). |
| Streamlit state synchronization | `selected_opportunity` and `resume_analysis` were not synced to `state` before calling `execute_action`. | Synchronized state in `app.py` across Opportunities, Resume, and Skill Builder tabs. |
| Cloud consent control | No explicit user toggle before cloud synthesis. | Added explicit consent checkbox in Skill Builder UI; routes to deterministic Python planner when consent is declined. |

---

## 4. Acceptance Readiness
All M6 requirements are implemented and verified with genuine model execution and end-to-end tests. Ready for M6 release tagging.
