# Google ADK Career Coordinator

This project uses Google ADK orchestration to sequence the specialized agent behaviors within the application.

### Architectural Principle

- **Gemini / Vertex AI**: Reasons and plans inside cloud environments.
- **Gemma 4 / Ollama**: Handles private resume intelligence locally, ensuring PII stays on your machine.
- **Python**: Verifies deterministic facts, performs strict gap analysis, and queries external APIs reliably.
- **Google ADK**: Coordinates the multi-agent workflow, managing state transitions and cleanly handling partial failures.

### Workflow Sequence

1. **Job Scout Agent**: Triggered to pull roles, extract requirements, and build a deterministic matching structure.
2. **Private Resume Agent**: Uses local Gemma to extract evidence mapped directly against the job requirements.
3. **Skill Builder Agent**: Takes extracted strengths and gaps, utilizing Python to prioritize learning topics and Gemini to map custom learning steps.

Google ADK guarantees that each transition passes only the required structured data, preserving a strict privacy boundary between the local and cloud runtimes.
