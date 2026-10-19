# uvx Installation & CLI Guide

This guide explains how to install and launch **Agentic Career Lab** using [`uvx`](https://docs.astral.sh/uv/guides/tools/) without manually setting up virtual environments or cloning the repository.

---

## ⚡ What is `uvx`?

`uvx` is a tool launcher bundled with [`uv`](https://docs.astral.sh/uv/), the fast Python package manager. It runs Python CLI applications in isolated, ephemeral virtual environments.

---

## 🛠️ Prerequisites

Before launching Agentic Career Lab, make sure you have:

1. **Python 3.11+**
2. **`uv` installed**:
   ```bash
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **Ollama running with Gemma 4**:
   Agentic Career Lab uses local Google Gemma 4 (`gemma4:12b`) for 100% private resume extraction and conversational guidance:
   ```bash
   # 1. Install Ollama (https://ollama.ai)
   # 2. Pull the Gemma 4 model:
   ollama pull gemma4:12b
   # 3. Start the Ollama server:
   ollama serve
   ```

---

## 🚀 Launching the Application

### Option A: From Built Wheel (Pre-PyPI / Local Distribution)

If testing from a pre-built wheel distribution file (e.g. from the `dist/` directory):

```bash
uvx --from ./dist/agentic_career_lab-0.10.1-py3-none-any.whl agentic-career-lab
```

### Option B: From PyPI (Post-Publication)

Once published to PyPI, you can launch the app directly with a single command:

```bash
uvx agentic-career-lab
```

The CLI will start the Streamlit server and provide the local URL:
```text
🚀 Starting Agentic Career Lab v0.10.1...
📍 Streamlit App: http://localhost:8501
💡 Press Ctrl+C to stop.
```

---

## 🩺 System Diagnostics (`doctor`)

To check whether your host machine meets all prerequisites (Python version, Ollama connectivity, Gemma 4 availability, and network ports):

```bash
# Pre-PyPI from wheel
uvx --from ./dist/agentic_career_lab-0.10.1-py3-none-any.whl agentic-career-lab doctor

# Post-PyPI
uvx agentic-career-lab doctor
```

Example doctor output:
```text
============================================================
Agentic Career Lab Doctor — v0.10.1
============================================================
[PASS]   Python Runtime: Python 3.11.6 (compatible >=3.11)
[PASS]   Package Application: Streamlit entry point verified
[PASS]   Streamlit Runtime: Streamlit v1.66.0 installed
[PASS]   Ollama Endpoint: Connected to http://localhost:11434 (HTTP 200)
[PASS]   Model (gemma4:12b): Model 'gemma4:12b' is pulled and ready in Ollama
[PASS]   Network Port (8501): Port 8501 is free to bind
------------------------------------------------------------
✅ All checks passed! Agentic Career Lab is fully ready to run.
```

---

## ⚙️ Environment Configuration

You can customize port and host bindings via standard environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `STREAMLIT_SERVER_PORT` | `8501` | Port for the Streamlit web interface |
| `STREAMLIT_SERVER_ADDRESS` | `localhost` | Network bind address |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service endpoint |
| `GEMMA_MODEL` | `gemma4:12b` | Local model name in Ollama |

Example:
```bash
STREAMLIT_SERVER_PORT=8502 OLLAMA_BASE_URL=http://192.168.1.50:11434 uvx agentic-career-lab
```

---

## 🔒 Privacy & Offline Boundaries

- **Zero Cloud Leakage:** In `uvx` mode, all processing runs locally on your host machine.
- **Local Ollama Inference:** Resumes and conversational state are processed strictly in memory by your local Gemma 4 model.
- **No Cloud Inference by Default:** Optional Gemini / Vertex AI cloud features remain blocked unless affirmative consent is granted.

---

## ❓ Troubleshooting

### Ollama Not Reachable (`[WARN] Ollama Endpoint`)
- **Fix:** Ensure Ollama is running (`ollama serve`) or check if your firewall blocks port `11434`.

### Model Missing (`[WARN] Model (gemma4:12b)`)
- **Fix:** Download the model via Ollama:
  ```bash
  ollama pull gemma4:12b
  ```

### Port In Use (`[WARN] Network Port (8501)`)
- **Fix:** If another service or container is using port 8501, Streamlit will automatically pick the next available port (e.g. 8502), or you can specify one:
  ```bash
  STREAMLIT_SERVER_PORT=8505 uvx agentic-career-lab
  ```
