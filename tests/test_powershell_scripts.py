"""QA tests for PowerShell scripts syntax and execution integrity on Windows."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent

PS_BIN = shutil.which("powershell") or shutil.which("pwsh")
HAS_POWERSHELL = PS_BIN is not None and sys.platform == "win32"

PS_SCRIPTS = [
    ROOT_DIR / "setup.ps1",
    ROOT_DIR / "scripts" / "install_context_menu.ps1",
    ROOT_DIR / "scripts" / "uninstall_context_menu.ps1",
    ROOT_DIR / "tools" / "system-backup-preformat" / "backup_preformat.ps1",
    ROOT_DIR / "tools" / "system-backup-preformat" / "template_reinstall.ps1",
    ROOT_DIR / "tools" / "vscode-path-doctor" / "check_vscode_path.ps1",
]


@pytest.mark.parametrize("script_path", PS_SCRIPTS, ids=lambda p: p.name)
def test_powershell_syntax_no_errors(script_path: Path):
    """Verify that PowerShell AST parser detects 0 syntax errors in each .ps1 file."""
    if not HAS_POWERSHELL:
        pytest.skip("PowerShell is not available on this platform.")

    assert script_path.exists(), f"Script {script_path} does not exist"

    # Run AST parser inside PowerShell
    ps_cmd = (
        f"$errs = $null; "
        f"[System.Management.Automation.Language.Parser]::ParseFile('{script_path.as_posix()}', [ref]$null, [ref]$errs); "
        f"if ($errs) {{ $errs | ForEach-Object {{ Write-Error $_.Message }} }}"
    )

    proc = subprocess.run(
        [PS_BIN, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert proc.returncode == 0, f"Syntax error in {script_path.name}:\n{proc.stderr}"
    assert "ParserError" not in proc.stderr
    assert "UnexpectedToken" not in proc.stderr


def test_check_vscode_path_execution():
    """Verify check_vscode_path.ps1 runs and exits with 0 on the current machine."""
    if not HAS_POWERSHELL:
        pytest.skip("PowerShell is not available on this platform.")

    script = ROOT_DIR / "tools" / "vscode-path-doctor" / "check_vscode_path.ps1"
    proc = subprocess.run(
        [PS_BIN, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    assert proc.returncode == 0
    assert "[DOCTOR] VS CODE PATH DIAGNOSTIC" in proc.stdout
    assert "ParserError" not in proc.stderr


def test_template_reinstall_nopause_execution():
    """Verify template_reinstall.ps1 executes without blocking when passed -NoPause."""
    if not HAS_POWERSHELL:
        pytest.skip("PowerShell is not available on this platform.")

    script = ROOT_DIR / "tools" / "system-backup-preformat" / "template_reinstall.ps1"
    proc = subprocess.run(
        [PS_BIN, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), "-NoPause"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    assert proc.returncode == 0
    assert "[SCRIPT-TOOLS]" in proc.stdout
    assert "ParserError" not in proc.stderr
