# Agentic Career Lab Roadmap

This roadmap outlines the planned development milestones following the **v0.10.0** release of **Agentic Career Lab**.

Our mission is to build an open-source, evidence-grounded, privacy-first career advancement platform that empowers students and developers to navigate modern career pathways without sacrificing data autonomy.

---

## 🗺️ Milestone Overview

```text
v0.10.0 (Released) ──► v0.11.0 (Resume Studio) ──► v0.12.0 (Persistent Workspace)
                             │                                 │
                             ▼                                 ▼
                     v0.13.0 (DevEx & CI) ─────────────► v0.14.0 (Job Integrations)
                                                               │
                                                               ▼
                                                     v0.15.0 (Learning Exp)
```

---

## 📍 Milestones & Planned Capabilities

### 🎨 v0.11.0 — Resume Studio
*Interactive, evidence-grounded resume improvement interface.*

- **Side-by-Side Diff Preview:** Render original resume text alongside agent-suggested improvements in real time.
- **Granular Approve / Reject Controls:** Allow students to accept individual bullet-point improvements, phrasing suggestions, or skill demonstrations.
- **Anti-Hallucination Guardrails:** Enforce strict grounding — reject attempts to fabricate non-existent roles, credentials, or unverifiable claims.
- **Multi-Format Export:** Export approved, tailored resumes directly to high-quality PDF and editable DOCX formats.

---

### 💾 v0.12.0 — Persistent Workspace
*Session-resilient local storage for uninterrupted career progression.*

- **Local SQLite Storage:** Secure, single-file SQLite database for student profiles, preferences, and target roles.
- **Chat History & Analysis Persistence:** Retain multi-turn conversations and previous resume evaluations across Streamlit restarts.
- **Learning Plan State Storage:** Persist checklist states, custom notes, and evidence artifacts across container reboots.
- **Data Export & Wipe Controls:** Provide a single-click "Purge All Data" mechanism to maintain total student data sovereignty.

---

### 🛠️ v0.13.0 — Developer Experience & Deployment
*Frictionless local onboarding, evaluation suites, and operational resilience.*

- **One-Command First-Run Setup:** Streamlined CLI bootstrap script verifying Ollama models, dependencies, and Docker containers.
- **Automated Agent Evaluation Suite:** Golden test dataset measuring faithfulness, hallucination rate, and action accuracy across agent responses.
- **Ollama Latency & Health Observability:** Proactive dashboard metrics surfacing local model warmup latency, memory consumption, and token generation speed.

---

### 🌐 v0.14.0 — Job Provider Integrations
*Live, diversified opportunity ingestion through modular provider contracts.*

- **Pluggable Job Provider Architecture:** Extend beyond mock listings with pluggable connectors (e.g., Hacker News "Who is Hiring", public ATS feeds, Open Job API).
- **Rate-Limiting & Caching:** Resilient caching and backoff handling to prevent duplicate scraping and external rate limits.
- **Prompt Injection Defense:** Strict sandboxing of retrieved job description text to prevent prompt injection attacks against LLM agents.

---

### 📚 v0.15.0 — Learning Experience
*Enhanced multimodal learning, accessibility, and mastery tracking.*

- **Full Keyboard Navigation & A11y:** WCAG 2.1 AA compliant UI with screen-reader friendly landmarks and high-contrast accessibility options.
- **Dynamic Resource Ingestion:** Ability for students to bookmark custom learning URLs with automatic metadata extraction.
- **Skill Mastery Verification:** Project-based rubrics and milestone checkpoints to independently verify acquired competencies.

---

## 🤝 How to Get Involved

We welcome community contributions across all milestones! If you're looking for a place to start:
- Look for issues labeled [`good first issue`](https://github.com/hastimal/agentic-career-lab/labels/good%20first%20issue) or [`help wanted`](https://github.com/hastimal/agentic-career-lab/labels/help%20wanted).
- Review our [Contributing Guide](../CONTRIBUTING.md) for local environment setup and quality requirements.
