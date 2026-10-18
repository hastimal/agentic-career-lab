# v0.9.0 Known Issues & Engineering Roadmap

This document outlines known limitations, pending refinements, and the future development roadmap for **Agentic Career Lab** following the completion of the v0.9.0 candidate release.

---

## ⚠️ Known Issues & Current Limitations (v0.9.0)

The following items represent known behaviors and architectural limitations in v0.9.0 that will be addressed in subsequent releases:

1. **Session-Bound Learning Progress**:
   - Weekly learning activity checkboxes and evidence notes persist cleanly within the student's active Streamlit session state.
   - However, progress is currently stored in memory and will not survive a container restart or browser session reset without an external database or local filesystem storage backend (targeted for v0.12.0).

2. **Technical Milestone Diagnostics**:
   - While developer OpenTelemetry trace data is now collapsed under diagnostics, some student milestone event labels in **Activity & Diagnostics** may still display low-level agent action nomenclature (e.g. `requirement_interpretation` or `claim_validation`) instead of purely conversational phrases.

3. **Grafana Observability Spans Panel**:
   - In specific local container setups, the Grafana *Recent Multi-Agent Spans* panel may experience latency querying Tempo traces via TraceQL (`{resource.service.name = "agentic-career-lab"}`).
   - Occasional transient "Unauthorized" notifications seen in Grafana dashboard loading require automated datasource credential pinning.

4. **Resource Icon Domain Availability**:
   - Compact learning cards map 40+ canonical providers and creators to high-resolution official favicons.
   - In fully offline or air-gapped environments without external internet connectivity, third-party favicons gracefully fall back to the neutral bookmark emoji (`🔖`) without affecting layout.

5. **Video Embed Privacy Boundaries**:
   - To prevent third-party tracking scripts, cookies, and oversized page loads, YouTube videos open directly in the verified destination via `Watch Video ↗` rather than embedded inline iframe players.

6. **Resume Studio Status**:
   - Resume Studio is currently an architectural specification and preview UI (`docs/features/resume-studio.md`). Automatic bullet diffs and resume document modifications are not yet enabled for student production use.

---

## 🗺️ Future Engineering Roadmap

### v0.10.0: AI Career Agent Chatbox & Interactive Coaching
- **Local-First Conversational Assistant**: Multi-turn career advising directly integrated into the Streamlit sidebar/drawer.
- **Google ADK Integration**: Structured tool calling enabling the conversational agent to query job opportunities, check skill prerequisites, and recommend tailored courses.
- **Resume Studio Foundation**: Initial schema and prompt engineering for conversational evidence gathering.

### v0.11.0: Evidence-Based Resume Revision Studio
- **Side-by-Side Bullet Diff Review**: Visual before-and-after comparison of suggested resume improvements based strictly on verified project evidence.
- **Human-in-the-Loop Safeguards**: Explicit student approval/rejection controls; zero automatic resume mutations.
- **ATS Export Upgrades**: Clean DOCX and PDF compilation with deterministic formatting.

### v0.12.0: Persistent Student Workspace & Evidence Storage
- **Persistent Workspace Engine**: Local SQLite / JSON-backed storage for student profiles, milestone progress, and evidence notes surviving container restarts.
- **Deliverable Portfolio Vault**: Local storage for capstone project code, Dockerfiles, and GitHub repository links.

### Future Stabilization & Enhancements
- **Enhanced Observability**: Production Tempo TraceQL optimization and automated health probes.
- **Extended Provider Ecosystem**: Additional verified hands-on lab environments and enterprise learning providers.
- **Expanded Evaluation Suite**: Automated synthetic student evaluation harness scoring recommendation relevance and evidence accuracy.
