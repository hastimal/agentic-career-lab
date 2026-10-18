# Security Policy

## Supported Versions

We provide security updates and critical fixes for the following versions of Agentic Career Lab:

| Version | Supported          |
| ------- | ------------------ |
| v0.10.x | :white_check_mark: |
| < v0.10 | :x:                |

---

## 🔒 Privacy & Security Commitments

Agentic Career Lab is architected around strict privacy-first data handling principles:

1. **Local-First Default:** All resume analysis, profile parsing, and conversational career guidance default to local model execution using Ollama (`gemma4:12b`).
2. **Explicit Cloud Consent:** Any optional cloud inference (e.g., Google Gemini) requires explicit, recorded user consent (`cloud_consent=True`).
3. **Zero Raw Resume Telemetry:** OpenTelemetry traces, Prometheus metrics, and application logs are sanitized to exclude raw resume text, PDF bytes, personal contact details, system prompts, and full LLM completions.
4. **Untrusted Data Isolation:** Job listings, externally scraped postings, and user uploads are treated as untrusted text and cannot inject system instructions into AI agents.

---

## Reporting a Vulnerability

If you discover a security vulnerability or privacy leak in Agentic Career Lab, please do **not** disclose it in a public GitHub issue.

Instead, please report security concerns privately:

- **Email:** `hastimal.jangid@gmail.com`
- **Subject:** `[SECURITY] Agentic Career Lab Vulnerability Report`

Please include:
- A description of the vulnerability or privacy bypass.
- Steps to reproduce or proof-of-concept code.
- Potential impact on student data, resume confidentiality, or host system security.
- Any suggested mitigations or patches.

You will receive an initial response acknowledging receipt within 48 hours. We will collaborate with you to evaluate the issue, produce a fix, and coordinate responsible disclosure.
