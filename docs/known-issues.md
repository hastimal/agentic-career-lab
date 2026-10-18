# v0.10.0 Known Issues & Engineering Roadmap

This document outlines known limitations, pending refinements, and the future development roadmap for **Agentic Career Lab** following the completion of the v0.10.0 candidate release.

---

## ⚠️ Known Issues & Current Limitations (v0.10.0)

The following items represent known behaviors and architectural limitations in v0.10.0 that will be addressed in subsequent releases:

1. **Session-Bound Chat & Learning State**:
   - Multi-turn conversation turns, weekly learning checkboxes, and evidence notes persist cleanly within the student's active Streamlit session state and survive page reruns.
   - However, progress and chat history are held in application memory and will not survive a container restart without an external database or local filesystem storage backend (targeted for v0.12.0).

2. **Resume Studio Status (Preview Only)**:
   - Resume Studio is currently an architectural specification and preview UI (`docs/features/resume-studio.md`). Automatic bullet diffs and resume document modifications are not yet enabled for student production use.

3. **Air-Gapped Favicon Fallback**:
   - Compact learning cards map 40+ canonical providers and creators to high-resolution official favicons.
   - In fully offline or air-gapped environments without external internet connectivity, third-party favicons gracefully fall back to the neutral bookmark emoji (`🔖`) without affecting layout.

4. **Local LLM Inference Latency**:
   - Initial cold-start queries against local Gemma 4 (12B parameters via Ollama) on CPU-only machines may take 60–90 seconds to load weights into memory.
   - Fine-grained token streaming and configurable 180s timeouts prevent disconnects while keeping the student informed with real-time status indicators.

---

## 🗺️ Future Engineering Roadmap

### v0.11.0: Evidence-Based Resume Revision Studio
- **Side-by-Side Bullet Diff Review**: Visual before-and-after comparison of suggested resume improvements based strictly on verified project evidence.
- **Human-in-the-Loop Safeguards**: Explicit student approval/rejection controls; zero automatic resume mutations.
- **ATS Export Upgrades**: Clean DOCX and PDF compilation with deterministic formatting.

### v0.12.0: Persistent Student Workspace & Evidence Storage
- **Persistent Workspace Engine**: Local SQLite / JSON-backed storage for student profiles, milestone progress, evidence notes, and chat transcripts surviving container restarts.
- **Deliverable Portfolio Vault**: Local storage for capstone project code, Dockerfiles, and GitHub repository links.

### Future Stabilization & Enhancements
- **Enhanced Observability**: Production Tempo TraceQL optimization and automated health probes.
- **Extended Provider Ecosystem**: Additional verified hands-on lab environments and enterprise learning providers.
- **Expanded Evaluation Suite**: Automated synthetic student evaluation harness scoring recommendation relevance and evidence accuracy.
