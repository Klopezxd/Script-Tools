"""Tests for tools.py master CLI dispatcher."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    """Runs tools.py with explicit UTF-8 encoding handling."""
    return subprocess.run(
        [sys.executable, str(ROOT_DIR / "tools.py")] + list(args),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_tools_help():
    """Verify that tools.py --help exits with code 0 and displays subcommands."""
    proc = run_tool("--help")
    assert proc.returncode == 0
    assert proc.stdout is not None
    assert "video" in proc.stdout
    assert "pdf" in proc.stdout
    assert "doctor" in proc.stdout
    assert "backup" in proc.stdout


def test_tools_version():
    """Verify that tools.py --version displays version and exits with 0."""
    proc = run_tool("--version")
    assert proc.returncode == 0
    assert "2.0.0" in proc.stdout


def test_tools_no_args():
    """Running tools.py with no args should print help and return 0."""
    proc = run_tool()
    assert proc.returncode == 0
    assert proc.stdout is not None
    assert "usage:" in proc.stdout


def test_tools_doctor_json():
    """Dispatching doctor with --json flag should return valid JSON."""
    proc = run_tool("doctor", "--json")
    assert proc.returncode == 0
    assert proc.stdout is not None
    data = json.loads(proc.stdout)
    assert isinstance(data, list)
    assert any(item.get("component", "").startswith("VS Code") for item in data)


def test_tools_video_missing_file():
    """Passing a non-existent video path must return code 1 immediately without blocking."""
    proc = run_tool("video", "nonexistent_video_path_xyz.mp4")
    assert proc.returncode == 1
    output = proc.stdout + proc.stderr
    assert "does not exist" in output.lower()


def test_tools_pdf_missing_file():
    """Passing a non-existent PDF path must return code 1 immediately without blocking."""
    proc = run_tool("pdf", "nonexistent_pdf_path_xyz.pdf")
    assert proc.returncode == 1
    output = proc.stdout + proc.stderr
    assert "no existe" in output.lower()


def test_tools_invalid_subcommand():
    """Passing an invalid subcommand must return non-zero error code and show help."""
    proc = run_tool("invalid_subcmd_xyz")
    assert proc.returncode in (1, 2)
    assert "usage:" in proc.stdout or "usage:" in proc.stderr


def test_tools_subcommands_help():
    """All subcommands must respond to --help cleanly."""
    for subcmd in ["video", "pdf", "doctor", "completion"]:
        proc = run_tool(subcmd, "--help")
        assert proc.returncode == 0
        assert "usage:" in proc.stdout or "usage:" in proc.stderr or "Uso:" in proc.stdout


def test_tools_completion_powershell():
    """Verify that tools completion powershell outputs valid Register-ArgumentCompleter snippet."""
    proc = run_tool("completion", "powershell")
    assert proc.returncode == 0
    assert "Register-ArgumentCompleter" in proc.stdout
    assert "video" in proc.stdout
    assert "pdf" in proc.stdout


def test_tools_completion_bash():
    """Verify that tools completion bash outputs complete -F function."""
    proc = run_tool("completion", "bash")
    assert proc.returncode == 0
    assert "complete -F _tools_completion" in proc.stdout


def test_tools_completion_zsh():
    """Verify that tools completion zsh outputs zsh compdef."""
    proc = run_tool("completion", "zsh")
    assert proc.returncode == 0
    assert "#compdef tools" in proc.stdout


def test_tools_completion_invalid():
    """Invalid shell name must return non-zero exit code with error message."""
    proc = run_tool("completion", "unknown_shell_xyz")
    assert proc.returncode == 1
    assert "no soportado" in proc.stderr
