"""CLI Launcher and Health Diagnostic Tool for Agentic Career Lab.

Supports starting the Streamlit application and running environment health checks:
    agentic-career-lab
    agentic-career-lab doctor
    agentic-career-lab --help
    agentic-career-lab --version
"""

import argparse
import importlib.util
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

from agentic_career_lab import __version__
from agentic_career_lab.config import settings


class CheckResult(NamedTuple):
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    message: str


def get_app_path() -> Path:
    """Resolve the absolute path to the packaged Streamlit app.py file."""
    spec = importlib.util.find_spec("agentic_career_lab.app")
    if spec and spec.origin:
        return Path(spec.origin).resolve()
    # Fallback to relative path from this module
    return (Path(__file__).parent / "app.py").resolve()


def check_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if the specified network port is available to bind."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def run_diagnostics(verbose: bool = False) -> list[CheckResult]:
    """Run environment, Ollama, model, and package diagnostics."""
    import httpx

    results: list[CheckResult] = []

    # 1. Python version check
    py_major, py_minor = sys.version_info[:2]
    if py_major == 3 and py_minor >= 11:
        results.append(
            CheckResult(
                name="Python Runtime",
                status="PASS",
                message=f"Python {py_major}.{py_minor}.{sys.version_info.micro} (compatible >=3.11)",
            )
        )
    else:
        results.append(
            CheckResult(
                name="Python Runtime",
                status="FAIL",
                message=f"Python {py_major}.{py_minor} is not supported. Please use Python 3.11+.",
            )
        )

    # 2. Package and assets check
    app_path = get_app_path()
    if app_path.exists() and app_path.is_file():
        results.append(
            CheckResult(
                name="Package Application",
                status="PASS",
                message=f"Streamlit entry point verified ({app_path})",
            )
        )
    else:
        results.append(
            CheckResult(
                name="Package Application",
                status="FAIL",
                message=f"Could not locate packaged app.py at {app_path}",
            )
        )

    # 3. Streamlit installation check
    try:
        import streamlit

        results.append(
            CheckResult(
                name="Streamlit Runtime",
                status="PASS",
                message=f"Streamlit v{streamlit.__version__} installed",
            )
        )
    except ImportError:
        results.append(
            CheckResult(
                name="Streamlit Runtime",
                status="FAIL",
                message="Streamlit is not installed in the active environment.",
            )
        )

    # 4. Ollama Connectivity
    ollama_url = os.environ.get("OLLAMA_BASE_URL", settings.ollama_base_url).rstrip("/")
    required_model = os.environ.get("GEMMA_MODEL", settings.gemma_model)
    ollama_connected = False
    available_models: list[str] = []

    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{ollama_url}/api/tags")
            if resp.status_code == 200:
                ollama_connected = True
                data = resp.json()
                for m in data.get("models", []):
                    name = m.get("name") or m.get("model")
                    if name:
                        available_models.append(name)
                results.append(
                    CheckResult(
                        name="Ollama Endpoint",
                        status="PASS",
                        message=f"Connected to {ollama_url} (HTTP 200)",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        name="Ollama Endpoint",
                        status="WARN",
                        message=f"Endpoint returned HTTP {resp.status_code} at {ollama_url}",
                    )
                )
    except httpx.ConnectError:
        results.append(
            CheckResult(
                name="Ollama Endpoint",
                status="WARN",
                message=(
                    f"Cannot connect to Ollama at {ollama_url}.\n"
                    "  -> Start native Ollama with: 'ollama serve'\n"
                    "  -> Or specify a custom host: export OLLAMA_BASE_URL=http://your-host:11434"
                ),
            )
        )
    except Exception as e:
        results.append(
            CheckResult(
                name="Ollama Endpoint",
                status="WARN",
                message=f"Error connecting to {ollama_url}: {e}",
            )
        )

    # 5. Gemma Model Availability
    if ollama_connected:
        # Check exact or prefix match (e.g., 'gemma4:12b' or 'gemma4:12b-latest')
        has_model = any(
            required_model in m or m.startswith(required_model) for m in available_models
        )
        if has_model:
            results.append(
                CheckResult(
                    name=f"Model ({required_model})",
                    status="PASS",
                    message=f"Model '{required_model}' is pulled and ready in Ollama",
                )
            )
        else:
            models_str = ", ".join(available_models) if available_models else "None"
            results.append(
                CheckResult(
                    name=f"Model ({required_model})",
                    status="WARN",
                    message=(
                        f"Model '{required_model}' not found in Ollama (found: {models_str}).\n"
                        f"  -> Pull it with: 'ollama pull {required_model}'"
                    ),
                )
            )
    else:
        results.append(
            CheckResult(
                name=f"Model ({required_model})",
                status="WARN",
                message=f"Skipped model check because Ollama is not connected at {ollama_url}.",
            )
        )

    # 6. Port 8501 availability
    port = int(os.environ.get("STREAMLIT_SERVER_PORT", "8501"))
    port_free = check_port_available(port)
    if port_free:
        results.append(
            CheckResult(
                name=f"Network Port ({port})",
                status="PASS",
                message=f"Port {port} is free to bind",
            )
        )
    else:
        results.append(
            CheckResult(
                name=f"Network Port ({port})",
                status="WARN",
                message=(
                    f"Port {port} is currently in use by another process.\n"
                    f"  -> Streamlit may automatically choose the next available port (e.g. {port + 1})"
                ),
            )
        )

    return results


def run_doctor_command() -> int:
    """Execute diagnostic checks and print human-readable status."""
    print("=" * 60)
    print(f"Agentic Career Lab Doctor — v{__version__}")
    print("=" * 60)

    results = run_diagnostics()
    has_fail = False
    has_warn = False

    for r in results:
        badge = f"[{r.status}]"
        print(f"{badge:<8} {r.name}: {r.message}")
        if r.status == "FAIL":
            has_fail = True
        elif r.status == "WARN":
            has_warn = True

    print("-" * 60)
    if has_fail:
        print("❌ Doctor found critical issues that will prevent the application from running.")
        return 1
    elif has_warn:
        print(
            "⚠️ Doctor found warnings. The application can start, but local AI reasoning may require starting Ollama."
        )
        return 0
    else:
        print("✅ All checks passed! Agentic Career Lab is fully ready to run.")
        return 0


def run_streamlit_app(args: list[str] | None = None) -> int:
    """Launch Streamlit application safely with the packaged app.py."""
    app_path = get_app_path()
    if not app_path.exists():
        sys.stderr.write(f"Error: Could not find packaged application file: {app_path}\n")
        return 1

    port = os.environ.get("STREAMLIT_SERVER_PORT", "8501")
    address = os.environ.get("STREAMLIT_SERVER_ADDRESS", "localhost")

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        f"--server.port={port}",
        f"--server.address={address}",
    ]
    if args:
        cmd.extend(args)

    print(f"🚀 Starting Agentic Career Lab v{__version__}...")
    print(f"📍 Streamlit App: http://{address}:{port}")
    print("💡 Press Ctrl+C to stop.")

    try:
        # Run subprocess without shell=True to prevent unsafe interpolation
        proc = subprocess.run(cmd)
        return proc.returncode
    except KeyboardInterrupt:
        print("\n👋 Stopping Agentic Career Lab. Goodbye!")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error launching Streamlit application: {e}\n")
        return 1


def main() -> None:
    """Entry point for the agentic-career-lab command."""
    parser = argparse.ArgumentParser(
        prog="agentic-career-lab",
        description="Agentic Career Lab: Privacy-First AI Career Assistant",
        epilog="Run 'agentic-career-lab doctor' to verify local Ollama and Gemma 4 prerequisites.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # doctor subcommand
    subparsers.add_parser(
        "doctor",
        help="Check local Python, Ollama, model, and network prerequisites",
    )

    # Parse arguments
    parsed_args, extra_args = parser.parse_known_args()

    if parsed_args.subcommand == "doctor":
        sys.exit(run_doctor_command())
    else:
        # Default behavior: run the Streamlit app
        sys.exit(run_streamlit_app(extra_args))


if __name__ == "__main__":
    main()
