"""#9: the Docker Compose preflight in scripts/setup.sh.

The failure this script exists to prevent shows up late and vaguely — an empty
Streamlit page because the container cannot reach Ollama, or a model that was
never pulled. So each prerequisite has to fail loudly and early, with the command
that fixes it.

These tests put stub binaries on PATH, so no Docker daemon, Ollama, model or
network is involved. `--dry-run` keeps the checks themselves real while the two
commands with side effects (a model pull, a compose run) are printed instead of
executed.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP = REPO_ROOT / "scripts" / "setup.sh"

DOCKER_OK = """\
if [ "$1" = "--version" ]; then echo "Docker version 27.3.1, build ce1223035a"; exit 0; fi
if [ "$1" = "info" ]; then exit 0; fi
if [ "$1" = "compose" ]; then
  if [ "$2" = "version" ]; then echo "2.29.7"; exit 0; fi
  echo "compose $*" >> "$STUB_LOG"
  exit 0
fi
exit 0
"""

DOCKER_DAEMON_DOWN = DOCKER_OK.replace(
    'if [ "$1" = "info" ]; then exit 0; fi',
    'if [ "$1" = "info" ]; then echo "Cannot connect to the Docker daemon" >&2; exit 1; fi',
)

OLLAMA_OK = """\
if [ "$1" = "list" ]; then
  printf 'NAME\\tID\\tSIZE\\n'
  printf '%s\\tdeadbeef\\t7.6 GB\\n' "$STUB_MODEL"
  exit 0
fi
exit 0
"""

OLLAMA_OTHER_MODEL = OLLAMA_OK.replace("$STUB_MODEL", "llama3.1:8b")


def _tools(**overrides: str) -> dict[str, str]:
    base = {
        "docker": DOCKER_OK,
        "uv": 'echo "uv 0.5.11"\n',
        "ollama": OLLAMA_OK,
        "nc": "exit 1\n",
    }
    for name, body in overrides.items():
        if body == "":
            base.pop(name, None)
        else:
            base[name] = body
    return base


def _run(tmp_path: Path, tools: dict[str, str], *args: str):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "stub.log"
    log.write_text("")
    for name, body in tools.items():
        stub = bin_dir / name
        stub.write_text("#!/usr/bin/env bash\n" + body)
        stub.chmod(0o755)
    env = {
        "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(tmp_path),
        "STUB_LOG": str(log),
        "STUB_MODEL": "gemma4:12b",
    }
    proc = subprocess.run(
        ["bash", str(SETUP), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
        stdin=subprocess.DEVNULL,
        timeout=60,
    )
    return proc, log.read_text()


def test_ready_prints_the_launch_command_and_touches_nothing(tmp_path):
    proc, calls = _run(tmp_path, _tools(), "--dry-run")

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "[PASS] ready" in proc.stdout
    assert "docker compose up -d --build" in proc.stdout
    assert "port 8501 is free" in proc.stdout
    # The connectivity check is printed rather than run, and nothing was launched.
    assert "(dry run) docker compose run" in proc.stdout
    assert calls == ""


def test_missing_uv_fails_with_the_install_command(tmp_path):
    proc, _ = _run(tmp_path, _tools(uv=""), "--dry-run")

    assert proc.returncode == 1
    assert "[FAIL] uv not found" in proc.stdout
    assert "astral.sh/uv" in proc.stdout


def test_stopped_docker_daemon_is_reported_separately(tmp_path):
    proc, _ = _run(tmp_path, _tools(docker=DOCKER_DAEMON_DOWN), "--dry-run")

    assert proc.returncode == 1
    assert "[FAIL] Docker daemon is not reachable" in proc.stdout
    # The CLI itself is fine; only the daemon is down.
    assert "[PASS] Docker CLI" in proc.stdout


def test_missing_model_names_the_exact_pull_command(tmp_path):
    proc, _ = _run(tmp_path, _tools(ollama=OLLAMA_OTHER_MODEL), "--dry-run", "--no-prompt")

    assert proc.returncode == 1
    assert "[FAIL] model gemma4:12b is not pulled" in proc.stdout
    assert "ollama pull gemma4:12b" in proc.stdout


def test_busy_port_suggests_the_override(tmp_path):
    proc, _ = _run(tmp_path, _tools(nc="exit 0\n"), "--dry-run")

    assert proc.returncode == 1
    assert "[FAIL] port 8501 is already in use" in proc.stdout
    assert "ACL_APP_PORT=8502 scripts/setup.sh" in proc.stdout


def test_port_and_model_can_be_overridden(tmp_path):
    proc, _ = _run(tmp_path, _tools(), "--dry-run", "--port", "8600")

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "port 8600 is free" in proc.stdout
    assert "port 8501 is free" not in proc.stdout


def test_help_lists_the_flags(tmp_path):
    proc, _ = _run(tmp_path, _tools(), "--help")

    assert proc.returncode == 0
    assert "--dry-run" in proc.stdout
    assert "--no-prompt" in proc.stdout


def test_both_quickstart_documents_point_at_the_script():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "scripts/setup.sh" in readme
    assert "scripts/setup.sh" in contributing


@pytest.mark.skipif(shutil.which("shellcheck") is None, reason="shellcheck is not installed")
def test_shellcheck_passes():
    proc = subprocess.run(
        ["shellcheck", "-S", "warning", str(SETUP)],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
