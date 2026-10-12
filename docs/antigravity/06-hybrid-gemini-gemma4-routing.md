# Milestone 6: Hybrid Gemini + Gemma Privacy Routing

## Architecture Principles
- **Google ADK**: Coordinates the multi-agent workflow deterministically without unnecessary LLM overhead.
- **Gemini / Vertex AI**: Synthesizes high-level learning roadmaps and practical portfolio projects from non-PII skill gaps.
- **Gemma 4 on Ollama**: Extracts resume evidence, maps requirements, and suggests rewrites 100% locally on user machines.
- **Python Determinism**: Computes exact gap statuses, claim validation, and resource matching.
- **Strict Privacy Boundary**: Typed `HybridRouter` and `assert_cloud_safe()` strictly prevent raw resume data and PII from reaching cloud models.
- **Explicit User Consent**: Skill Builder requires explicit opt-in before sharing sanitized skill gap names with Cloud AI, providing local deterministic Python fallback when declined.

## Routing Policy Summary
| Task Type | Target Runtime | Privacy Level | Cloud Allowed | Fallback Allowed |
|---|---|---|---|---|
| `OPPORTUNITY_SEARCH` | Python / Adzuna / Mock | Public | Yes | Yes |
| `RESUME_ANALYSIS` | Gemma 4 / Ollama | Private | **No** | **No** |
| `RESUME_REWRITE` | Gemma 4 / Ollama | Private | **No** | **No** |
| `CLAIM_VALIDATION` | Python (Deterministic) | Structured | **No** | **No** |
| `GAP_ANALYSIS` | Python (Deterministic) | Structured | **No** | **No** |
| `LEARNING_PLAN` | Gemini / Vertex AI | Structured | Yes | Yes |
| `PORTFOLIO_PROJECT` | Gemini / Vertex AI | Structured | Yes | Yes |
| `RESOURCE_LOOKUP` | Python (Catalog) | Public | **No** | **No** |

## Verification
- Acceptance Report: [m6-demo-acceptance.md](m6-demo-acceptance.md)
- Audit Report: [m6-demo-audit.md](m6-demo-audit.md)
- Smoke Test: `python scripts/smoke_resume_local.py <resume_path>`
