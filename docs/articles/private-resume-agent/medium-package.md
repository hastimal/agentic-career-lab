# Medium Publishing Package

This document contains publication assets, social copy, metadata, and checklist items for publishing the revised technical article **"Building a Private AI Resume Agent with Gemma 4, Ollama, and Docker"** to Medium and the Google Cloud Community.

---

## 📌 Article Metadata

- **Article Title**: Building a Private AI Resume Agent with Gemma 4, Ollama, and Docker
- **Subtitle**: How to architect, deploy, and trace privacy-first career intelligence on local hardware without sending sensitive candidate resumes to cloud models.
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

We have prepared high-resolution 16:9 (1672 × 941) cover art tailored for Medium and Google Cloud Community headers:

1. **Recommended Hero Cover (`assets/cover-art-architecture.png`)**:
   - Modern isometric architectural rendering showcasing Gemma 4, Ollama, Docker containers, and OpenTelemetry instrumentation.
   - Clean, professional styling with Google Cloud and privacy-first visual motifs.
   - Alt text: *Isometric architecture visualization of a private AI agent stack running Gemma 4, Ollama, Docker, and OpenTelemetry.*
2. **Alternative Dark Variant (`assets/cover-art-dark.png`)**:
   - High-contrast developer-centric aesthetic suitable for technical publications.
3. **Alternative Minimal Variant (`assets/cover-art-minimal.png`)**:
   - Minimalist illustration focusing on the privacy firewall boundary.

---

## 📸 Medium Image Insertion Order

Embed the images in your Medium draft in the following order:

| Visual | File Path | In-Article Section | Caption |
| :---: | :--- | :--- | :--- |
| **Figure 1** | `assets/diagram-a-private-resume-architecture.png` | Section 2 | *Figure 1: Private Resume Processing Architecture. Raw resume documents are parsed in volatile memory inside Docker and evaluated by native Ollama running Gemma 4 on the host machine.* |
| **Figure 2** | `assets/ui-my-resume.png` | Section 6 | *Figure 2: The Streamlit My Resume view. Displays uploaded resume confirmation, local memory parsing, privacy notice, and local Gemma 4 evidence extraction triggers.* |
| **Figure 3** | `assets/ui-skill-gap-analysis.png` | Section 6 | *Figure 3: Skill Gap Analysis view. Shows transparent three-category breakdown: Demonstrated Strengths (verified with resume evidence), Mentioned/Partial Skills, and Missing Requirements.* |
| **Figure 4** | `assets/diagram-b-privacy-observability.png` | Section 7 | *Figure 4: Observability and Privacy Architecture. OpenTelemetry spans are sanitized in-app, exported over OTLP gRPC to the Collector, and routed to Tempo and Prometheus. Optional cloud reasoning is gated by explicit user consent.* |
| **Figure 5** | `assets/tempo-trace-waterfall.png` | Section 9 | *Figure 5: Grafana Tempo trace waterfall for `coordinator.prepare_resume` (Trace ID `947c2209b3513394471ff14a0675c9ec`). Illustrates the four-span hierarchy across the coordinator, private resume agent, and two distinct Ollama inference calls.* |

---

## 📢 Suggested Social Announcements

### LinkedIn Announcement

```markdown
Building an AI resume assistant sounds simple: upload a resume, call an LLM, and return a skills summary.

But where does that resume go, and what happens when the application needs cloud services, logs, and distributed tracing?

Prompt engineering alone ("please do not store this data") is not an architectural defense. In our latest engineering deep dive, we walk through how we solved this in Agentic Career Lab:

🔹 Local Inference with Gemma 4: Extracting structured skills and experience directly on the host workstation using Ollama (leveraging Apple Silicon Metal acceleration).
🔹 Architectural Privacy Boundaries: Raw resumes are parsed in volatile session state; optional cloud reasoning (Gemini Flash) only receives allowlisted metadata tokens with explicit user consent.
🔹 Production Docker Stack: Containerized Streamlit UI bridged to host-native Ollama via host.docker.internal.
🔹 Observability Without Data Leakage: Sanitized OpenTelemetry tracing pipeline (OTel Collector -> Grafana Tempo -> Prometheus) with automatic denylist attribute filtering.
🔹 Authentic Trace Evidence: Analyzing real 4-span Tempo waterfalls (101.0s duration) showing exact latency distribution across sequential inference calls.

Read the full engineering article: [ARTICLE_LINK]
GitHub Repository: https://github.com/hastimal/agentic-career-lab

#Gemma #Ollama #Docker #OpenTelemetry #Privacy #GenerativeAI #GoogleCloud #AIArchitecture
```

### X / Twitter Thread Starter

```markdown
1/8 Building an AI resume assistant sounds simple: upload a document, call an LLM, return a skills summary.

But where does that resume go? And what happens when you need logs and distributed traces?

Here is how we architected a private resume agent with Gemma 4, Ollama, Docker, and OpenTelemetry 🧵👇
```

---

## 📝 Markdown-to-Medium Publishing Checklist

1. **Import via Medium Story Importer**:
   - Navigate to `medium.com/p/import`.
   - Provide the raw GitHub URL or paste the Markdown directly.
2. **Use Pre-Rendered High-Resolution PNGs**:
   - Medium does not render SVG files.
   - All article diagrams have already been rendered to crisp 16:9 1600×900 PNGs in `docs/articles/private-resume-agent/assets/`.
3. **Format Code Blocks**:
   - Ensure syntax highlighting is set to `Python`, `YAML`, or `Bash`.
   - All code snippets are labeled with their origin file and line ranges.
4. **Verify Hyperlinks**:
   - Confirm all links to `github.com/hastimal/agentic-career-lab` resolve cleanly.
5. **Set Canonical Link**:
   - Go to **Story Settings → Advanced Settings → Customize Canonical Link**.
   - Set to your portfolio or original GitHub documentation URL.
