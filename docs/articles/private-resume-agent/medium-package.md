# Medium Publishing Package

This document contains publication assets, social copy, metadata, and checklist items for publishing the technical article **"Building a Private AI Resume Agent with Gemma 4, Ollama, and Docker"** to Medium and Google Cloud Community.

---

## 📌 Article Metadata

- **Article Title**: Building a Private AI Resume Agent with Gemma 4, Ollama, and Docker
- **Subtitle**: How to build production-grade, privacy-first career intelligence on local hardware with zero resume leakage to cloud language models.
- **SEO Title**: Private AI Resume Agent with Gemma 4, Ollama & Docker
  *(58 characters - fits ~60 character maximum)*
- **SEO Description**: Architect and trace a private resume AI agent using local Gemma 4, Ollama, Docker Compose, and OpenTelemetry without leaking PII to cloud models.
  *(154 characters - fits ~140–160 character recommendation)*
- **Canonical URL**: `https://github.com/hastimal/agentic-career-lab/blob/main/docs/articles/private-resume-agent/article.md`
- **Target Publications**: Medium (Google Cloud Community, Towards Data Science, Better Programming, Level Up Coding)

---

## 🏷️ Medium Topics / Tags

Select up to 5 tags in the Medium story settings:
1. `Gemma`
2. `Ollama`
3. `Docker`
4. `Generative AI`
5. `OpenTelemetry`

*(Alternative secondary tags: `Privacy`, `DevOps`, `Machine Learning`)*

---

## 🖼️ Suggested Cover Image

- **Recommended Primary Asset**: `assets/privacy-boundary.svg` (or exported PNG `assets/privacy-boundary.png`)
- **Alternative Asset**: `assets/tempo-trace.png` (displays authentic OpenTelemetry waterfall)
- **Alt Text**: *Architectural diagram contrasting local resume analysis inside Ollama against optional sanitized cloud synthesis.*
- **Image Caption**: *Architecture of Agentic Career Lab: Strict separation between local private execution and optional cloud reasoning.*

---

## 📸 Medium Image Insertion Order

Embed images in the Medium draft in the following order:

| Visual | File Path | In-Article Section | Caption |
| :---: | :--- | :--- | :--- |
| **Figure 1** | `assets/system-architecture.svg` | Section 2 | *High-level multi-agent architecture of Agentic Career Lab, illustrating task separation across Job Scout, Private Resume Agent, and Skill Builder.* |
| **Figure 2** | `assets/privacy-boundary.svg` | Section 2 | *The structural privacy firewall. Raw resumes are parsed in volatile RAM and evaluated exclusively by local Gemma 4. Cloud synthesis engines receive sanitized skill gap tokens only when consent is granted.* |
| **Figure 3** | `assets/ui-my-resume.png` | Section 4 | *The Streamlit My Resume view. Displays uploaded resume confirmation, local memory parsing, privacy notice, and local Gemma 4 evidence extraction.* |
| **Figure 4** | `assets/docker-architecture.svg` | Section 6 | *Complete Docker Compose topology. The application container bridges to host-native Ollama via `host.docker.internal:11434` and exports telemetry to the local observability stack.* |
| **Figure 5** | `assets/tempo-trace.png` | Section 8 | *Grafana Tempo trace waterfall for `coordinator.prepare_resume` (Trace ID `683d9afbcad39c179c29cf914682fc42`). Spans illustrate end-to-end execution across the coordinator, agent, and Ollama inference layer.* |
| **Figure 6** | `assets/grafana-dashboard.png` | Section 8 | *Real-time Grafana dashboard monitoring agent request rates, p95 execution latency, and error rates without logging PII.* |

---

## 📢 Suggested Social Announcements

### LinkedIn Announcement

```markdown
How do you build AI resume analysis without sending sensitive personal resumes to a cloud LLM?

Prompting a model with "please do not store this" is not a privacy strategy. Privacy must be enforced by architecture.

In my latest technical deep dive, I break down how we built the Private Resume Agent in Agentic Career Lab:

🔹 Local Inference with Gemma 4: Extracting structured skills and experience directly on the host using Ollama (Metal GPU-accelerated on Apple Silicon).
🔹 Structural Privacy Boundary: Raw resumes remain in volatile memory; optional cloud engines (like Gemini Flash) only receive sanitized skill gap tokens (e.g., ["Docker", "Kubernetes"]) with explicit user consent.
🔹 Production Docker Stack: Containerized Streamlit UI bridged to native host Ollama via host.docker.internal.
🔹 Zero-Leakage Observability: Full OpenTelemetry tracing pipeline (OTel Collector -> Grafana Tempo -> Prometheus) with automatic sanitization of prompts, responses, and candidate PII.

Includes real code excerpts, reproducible Docker Compose setups, and authentic distributed trace waterfalls.

Read the full breakdown: [ARTICLE_LINK]
Open source repo on GitHub: https://github.com/hastimal/agentic-career-lab

#Gemma #Ollama #Docker #OpenTelemetry #Privacy #GenerativeAI #GoogleCloud #AIArchitecture
```

### X / Twitter Thread Starter

```markdown
1/7 Can you build a production-grade AI resume agent without shipping candidate resumes to cloud APIs?

Yes. But you can't rely on prompt engineering. Privacy must be enforced by architecture.

Here is how we built it using Google's Gemma 4, Ollama, Docker, and OpenTelemetry 🧵👇
```

---

## 📝 Markdown-to-Medium Publishing Checklist

1. **Import via Medium Story Importer**:
   - Navigate to `medium.com/p/import`.
   - Provide the raw GitHub URL or paste the Markdown directly.
2. **Convert SVGs to High-Resolution PNGs for Medium**:
   - Medium does not natively render SVG images.
   - Convert `system-architecture.svg`, `privacy-boundary.svg`, and `docker-architecture.svg` into PNG format using standard macOS tools:
     ```bash
     qlmanage -t -s 2000 -o docs/articles/private-resume-agent/assets/ docs/articles/private-resume-agent/assets/*.svg
     ```
3. **Format Code Blocks**:
   - Ensure syntax highlighting is set to `Python`, `YAML`, or `Bash`.
   - Medium supports triple backtick code blocks with automatic formatting.
4. **Verify Hyperlinks**:
   - Confirm all links to `github.com/hastimal/agentic-career-lab` resolve cleanly.
5. **Set Canonical Link**:
   - Go to **Story Settings → Advanced Settings → Customize Canonical Link**.
   - Set to your portfolio or original GitHub documentation URL.

