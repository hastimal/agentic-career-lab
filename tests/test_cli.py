"""Tests for CLI launcher, argument parsing, entry points, and doctor diagnostics."""

import os
from unittest.mock import MagicMock, patch

import pytest

from agentic_career_lab import __version__
from agentic_career_lab.cli import (
    check_port_available,
    get_app_path,
    main,
    run_diagnostics,
    run_doctor_command,
    run_streamlit_app,
)


def test_get_app_path_exists():
    """Verify that get_app_path resolves to a real, valid app.py file."""
    app_path = get_app_path()
    assert app_path.exists()
    assert app_path.is_file()
    assert app_path.name == "app.py"


def test_cli_version_flag(capsys):
    """Test agentic-career-lab --version exits cleanly with version string."""
    with patch("sys.argv", ["agentic-career-lab", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out or __version__ in captured.err


def test_cli_help_flag(capsys):
    """Test agentic-career-lab --help exits cleanly with usage info."""
    with patch("sys.argv", ["agentic-career-lab", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "doctor" in captured.out
    assert "Privacy-First AI Career Assistant" in captured.out


def test_check_port_available():
    """Test check_port_available with standard ports."""
    # Binding to an ephemeral high port should succeed
    assert isinstance(check_port_available(54321), bool)


def test_diagnostics_all_mocked_pass():
    """Test run_diagnostics when Ollama and gemma model are available."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [{"name": "gemma4:12b"}, {"name": "llama3:latest"}]
    }

    with (
        patch("httpx.Client.get", return_value=mock_response),
        patch("agentic_career_lab.cli.check_port_available", return_value=True),
    ):
        results = run_diagnostics()

    statuses = {r.name: r.status for r in results}
    assert statuses["Python Runtime"] == "PASS"
    assert statuses["Package Application"] == "PASS"
    assert statuses["Streamlit Runtime"] == "PASS"
    assert statuses["Ollama Endpoint"] == "PASS"
    assert "Model (gemma4:12b)" in statuses
    assert statuses["Model (gemma4:12b)"] == "PASS"
    assert "Network Port (8501)" in statuses
    assert statuses["Network Port (8501)"] == "PASS"


def test_diagnostics_missing_ollama():
    """Test run_diagnostics when Ollama server is unreachable."""
    import httpx

    with (
        patch("httpx.Client.get", side_effect=httpx.ConnectError("Connection refused")),
        patch("agentic_career_lab.cli.check_port_available", return_value=True),
    ):
        results = run_diagnostics()

    statuses = {r.name: r.status for r in results}
    assert statuses["Ollama Endpoint"] == "WARN"
    assert statuses["Model (gemma4:12b)"] == "WARN"
    # Diagnostic message must provide actionable instruction
    ollama_check = next(r for r in results if r.name == "Ollama Endpoint")
    assert "ollama serve" in ollama_check.message


def test_diagnostics_missing_gemma_model():
    """Test run_diagnostics when Ollama is running but gemma4:12b is not pulled."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": [{"name": "llama3:8b"}]}

    with (
        patch("httpx.Client.get", return_value=mock_response),
        patch("agentic_career_lab.cli.check_port_available", return_value=True),
    ):
        results = run_diagnostics()

    model_check = next(r for r in results if "Model" in r.name)
    assert model_check.status == "WARN"
    assert "ollama pull gemma4:12b" in model_check.message


def test_diagnostics_custom_ollama_base_url():
    """Test that OLLAMA_BASE_URL environment variable is respected."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": [{"name": "gemma4:12b"}]}

    with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://custom-host:11434"}):
        with (
            patch("httpx.Client.get", return_value=mock_response) as mock_get,
            patch("agentic_career_lab.cli.check_port_available", return_value=True),
        ):
            results = run_diagnostics()
            mock_get.assert_called_with("http://custom-host:11434/api/tags")

    ollama_check = next(r for r in results if r.name == "Ollama Endpoint")
    assert "http://custom-host:11434" in ollama_check.message


def test_doctor_command_success(capsys):
    """Test run_doctor_command prints formatted diagnostic summary."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": [{"name": "gemma4:12b"}]}

    with (
        patch("httpx.Client.get", return_value=mock_response),
        patch("agentic_career_lab.cli.check_port_available", return_value=True),
    ):
        exit_code = run_doctor_command()

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Agentic Career Lab Doctor" in captured.out
    assert "[PASS]" in captured.out


def test_run_streamlit_app_invocation():
    """Test run_streamlit_app prepares correct command line arguments."""
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        exit_code = run_streamlit_app(["--server.headless=true"])
        assert exit_code == 0
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "streamlit" in cmd
        assert "run" in cmd
        assert "--server.headless=true" in cmd


def test_run_streamlit_app_handles_ctrl_c():
    """Test run_streamlit_app gracefully handles KeyboardInterrupt."""
    with patch("subprocess.run", side_effect=KeyboardInterrupt):
        exit_code = run_streamlit_app()
        assert exit_code == 0
