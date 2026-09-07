"""QA unit tests for Developer Doctor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tools" / "vscode-path-doctor"))

from dev_doctor import (
    CheckResult,
    audit_compilers,
    audit_git,
    audit_multimedia,
    audit_runtimes,
    audit_vscode,
)


def test_check_result_structure():
    """Verify CheckResult dataclass behavior and attributes."""
    res = CheckResult(
        category="TestCat",
        component="TestComp",
        status="OK",
        details="Working fine",
        recommendation=None,
    )
    assert res.category == "TestCat"
    assert res.component == "TestComp"
    assert res.status == "OK"
    assert res.details == "Working fine"
    assert res.recommendation is None


def test_audit_functions_return_types():
    """Verify that all audit functions return lists of valid CheckResult objects."""
    for audit_fn in [audit_vscode, audit_git, audit_compilers, audit_runtimes, audit_multimedia]:
        results = audit_fn()
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert isinstance(r, CheckResult)
            assert r.status in ("OK", "WARN", "MISSING")
            assert len(r.component) > 0
            assert len(r.details) > 0


def test_dev_doctor_json_exportability():
    """Verify that audit results can be serialized cleanly to JSON without error."""
    results = audit_runtimes() + audit_git()
    data = [
        {
            "category": c.category,
            "component": c.component,
            "status": c.status,
            "details": c.details,
            "recommendation": c.recommendation,
        }
        for c in results
    ]
    serialized = json.dumps(data)
    deserialized = json.loads(serialized)
    assert len(deserialized) == len(results)
    assert deserialized[0]["category"] in ["Runtimes", "VCS"]


def test_check_command_nonexistent():
    """Verify check_command returns False gracefully for non-existent binaries."""
    from dev_doctor import check_command

    success, msg = check_command("nonexistent_binary_xyz_12345", ["--version"])
    assert success is False
    assert "No encontrado" in msg
