# Cross-Platform `uvx` Installation & CLI Reference

This document provides complete instructions for installing and running **Agentic Career Lab** across **Windows**, **macOS**, and **Linux** using [`uvx`](https://docs.astral.sh/uv/guides/tools/).

---

## ⚡ What is `uvx`?

`uvx` is a tool launcher bundled with [`uv`](https://docs.astral.sh/uv/), Astral's high-performance Python package manager.

**Key Characteristics of `uvx`:**
- **Isolated, Cached Environments:** `uvx` installs the package and its dependencies into an isolated cached virtual environment on demand rather than installing them into your global system Python.
- **No Manual Virtualenv Setup:** You do not need to run `python -m venv` or manage virtual environment activations.
- **Automatic Python Management:** If your system lacks Python >=3.11, `uv` downloads and manages a compatible Python runtime automatically.
- **Index Resolution:** Running `uvx --refresh agentic-career-lab` forces `uv` to check the current PyPI index for the latest releases.

---

## 🛠️ A. Prerequisites

Before launching Agentic Career Lab, ensure you have:
1. **`uv` / `uvx`**: The fast Python tool runner.
2. **Ollama**: Local inference engine for private AI.
3. **`gemma4:12b` model**: Offline LLM for private resume intelligence and mentor chat.
4. **Network connectivity**: Required only for initial package download and model weights.

---

## 🪟 B. Windows (PowerShell) Installation

### Step 1: Install `uv`
Open Windows PowerShell (Run as Administrator is optional, standard user works):
```powershell
winget install --id astral-sh.uv -e
```
*Alternative standalone PowerShell script:*
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Restart PowerShell
Close and reopen your PowerShell terminal to ensure environment variables (`PATH`) reload.

### Step 3: Verify `uv` and `uvx`
```powershell
uv --version
uvx --version
```

### Step 4: Install Ollama for Windows
Download and run the official Windows installer:
[https://ollama.com/download/windows](https://ollama.com/download/windows)

### Step 5: Pull Gemma 4
```powershell
ollama pull gemma4:12b
```

### Step 6: Verify with Doctor Diagnostics
```powershell
uvx agentic-career-lab doctor
```

### Step 7: Launch Application
```powershell
uvx agentic-career-lab
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🍎 C. macOS Installation

### Step 1: Install `uv`
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*Restart terminal or source your profile (`source ~/.zshrc` or `source ~/.bash_profile`) if needed.*

### Step 2: Verify `uvx`
```bash
uvx --version
```

### Step 3: Install Ollama for macOS
Download and install the native macOS app:
[https://ollama.com/download/mac](https://ollama.com/download/mac)

### Step 4: Pull Model, Run Doctor, and Launch
```bash
# Pull model
ollama pull gemma4:12b

# Run diagnostics
uvx agentic-career-lab doctor

# Launch app
uvx agentic-career-lab
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🐧 D. Linux Installation

> ⚠️ *Note: Linux package installation varies by distribution. Use the official installer or your distribution's native package manager.*

### Step 1: Install `uv`
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*Reload your shell session (`source ~/.bashrc` or `source ~/.zshrc`).*

### Step 2: Verify `uvx`
```bash
uvx --version
```

### Step 3: Install Ollama for Linux
Follow official instructions at [https://ollama.com/download/linux](https://ollama.com/download/linux):
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 4: Pull Model, Run Doctor, and Launch
```bash
ollama pull gemma4:12b
uvx agentic-career-lab doctor
uvx agentic-career-lab
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🤖 E. Ollama and Gemma 4 Setup

Agentic Career Lab relies on local Ollama for all private intelligence:
- **Default Endpoint:** `http://localhost:11434`
- **Required Model:** `gemma4:12b` (approx. 8 GB download; requires ~10-12 GB RAM / VRAM).

To manage the model:
```bash
# Verify model is available locally
ollama list

# Update or pull model
ollama pull gemma4:12b

# Test interactive generation
ollama run gemma4:12b "Explain 3 key skills for cloud engineers."
```

---

## 🩺 F. Doctor Diagnostics

The built-in diagnostic tool validates host prerequisites before launching:
```bash
uvx agentic-career-lab doctor
```

### Sample Output:
```text
============================================================
Agentic Career Lab Doctor — v0.10.2
============================================================
[PASS]   Python Runtime: Python 3.12.15 (compatible >=3.11)
[PASS]   Package Application: Streamlit entry point verified
[PASS]   Streamlit Runtime: Streamlit v1.66.0 installed
[PASS]   Ollama Endpoint: Connected to http://localhost:11434 (HTTP 200)
[PASS]   Model (gemma4:12b): Model 'gemma4:12b' is pulled and ready in Ollama
[PASS]   Network Port (8501): Port 8501 is free to bind
------------------------------------------------------------
✅ All checks passed! Agentic Career Lab is fully ready to run.
```

---

## 🚀 G. Launch Instructions & Options

### Standard PyPI Launch:
```bash
uvx agentic-career-lab
```

### Force Index Refresh:
To bypass cached wheel resolutions and ensure you run the newest PyPI release:
```bash
uvx --refresh agentic-career-lab
```

### Alternative `uv tool run` syntax:
```bash
uv tool run agentic-career-lab
```

### Custom Port & Address:
```bash
# Linux / macOS
STREAMLIT_SERVER_PORT=8505 STREAMLIT_SERVER_ADDRESS=0.0.0.0 uvx agentic-career-lab

# Windows PowerShell
$env:STREAMLIT_SERVER_PORT="8505"
uvx agentic-career-lab
```

---

## ❓ H. Troubleshooting Guide

### 1. `ERROR: 'uvx' is not recognized as an internal or external command` (Windows)
- **Cause:** `uv` is not installed, or the install directory is not in your system `PATH`, or PowerShell was not restarted.
- **Fix:**
  1. Restart PowerShell.
  2. If still not found, check if `%USERPROFILE%\.local\bin` or `%USERPROFILE%\AppData\Local\Programs\astral-sh\uv` is in your `PATH`.
  3. Try using `uv tool run agentic-career-lab` if `uv` is found but `uvx` is not.

### 2. `ERROR: 'ollama' is not recognized` (Windows / Linux)
- **Cause:** Ollama was installed while PowerShell was open, or the Ollama service is not running.
- **Fix:**
  1. Restart PowerShell or your terminal.
  2. Launch the Ollama desktop app from the Start Menu (Windows) or Applications (macOS).
  3. Verify by running `ollama --version`.

### 3. `[WARN] Model (gemma4:12b): Model is not pulled`
- **Cause:** The model has not been downloaded yet.
- **Fix:**
  ```bash
  ollama list
  ollama pull gemma4:12b
  ```

### 4. `[WARN] Ollama Endpoint: Connection refused`
- **Cause:** Ollama background daemon is stopped.
- **Fix:**
  - **macOS / Windows:** Open the Ollama application.
  - **Linux:** Run `systemctl start ollama` or `ollama serve`.

### 5. `[WARN] Network Port (8501): Port is currently in use`
- **Cause:** Another process (e.g. Docker, another Streamlit instance) is bound to 8501.
- **Windows Inspection:**
  ```powershell
  Get-NetTCPConnection -LocalPort 8501 -State Listen
  ```
  *(Do not terminate unrelated processes automatically).*
- **Resolution:** Provide an alternate port:
  ```powershell
  $env:STREAMLIT_SERVER_PORT="8502"; uvx agentic-career-lab
  ```

### 6. `ERROR: Python not installed or version too low`
- **Clarification:** `uv` can install and manage isolated Python runtimes automatically without requiring a separate system-wide Python installer.
- **Fix:**
  ```bash
  uv python install 3.12
  uvx --python 3.12 agentic-career-lab
  ```

### 7. Slow Gemma 4 Inference
- **Cause:** Gemma 4 (11.9B parameters) requires sufficient RAM and compute. On machines without supported GPU acceleration (e.g. Apple Silicon Metal or NVIDIA CUDA), inference falls back to CPU, which is substantially slower.
- **Guidance:**
  - Ensure at least 16 GB of system RAM.
  - Close memory-heavy applications during resume analysis.
  - Performance varies based on host hardware; GPU acceleration is not guaranteed on all configurations.

---

## 🔄 I. Updating the Package

To update to the newest version published on PyPI:
```bash
uvx --refresh agentic-career-lab
```

---

## 🧹 J. Removing the Package & Cleaning Cache

Because `uvx` does not modify system files, cleaning is trivial:
```bash
# Clean cached tool environments
uv cache clean

# View installed Python tools
uv tool list
```

---

## ⚠️ K. Known Platform Limitations

| Platform | Known Considerations |
| :--- | :--- |
| **Windows** | PowerShell execution policy may require `-ExecutionPolicy Bypass` for one-line installer. Hardware-accelerated inference requires NVIDIA GPU with modern drivers; CPU-only execution will have higher latency. |
| **Linux** | Headless servers require running with `STREAMLIT_SERVER_HEADLESS=true`. Port 8501 firewall rules must allow inbound traffic if accessing from a remote browser. |
| **macOS** | Runs natively with unified memory GPU acceleration on Apple Silicon (M1/M2/M3/M4). Intel Macs fall back to CPU inference. |

---

## ⚖️ L. Docker versus `uvx` Comparison

| Dimension | `uvx` Launcher Mode | Docker Compose Mode |
| :--- | :--- | :--- |
| **Target User** | Students & quick adopters | Platform developers & DevOps |
| **Docker Required** | ❌ No | ✅ Yes |
| **Git Clone Required** | ❌ No | ✅ Yes |
| **Startup Time** | ~1-3 seconds (cached) | ~30-60 seconds (containers) |
| **Telemetry & Observability** | Console & local logging | Full stack: Prometheus, Grafana, Tempo |
| **Model Hosting** | Host Ollama | Host Ollama (bridged via `host.docker.internal`) |

---

## 🔒 M. Privacy and Optional Cloud Features

- **Private by Default:** All resume parsing, skill matching, and conversational assistance run strictly on your local machine.
- **Zero Cloud Leakage:** No resume text or PII is sent to external cloud APIs by default.
- **Deterministic Offline Fallback:** If Ollama is unavailable or cloud consent is disabled, the application utilizes its built-in deterministic planning algorithms and 104-item vetted curriculum catalog.
