"""Tests for multiplatform backup_unix module."""

from __future__ import annotations

from unittest.mock import patch

from backup_unix import backup_unix


def test_backup_unix_mocked(tmp_path):
    """Test that backup_unix creates directory and expected structure."""
    with patch("pathlib.Path.home", return_value=tmp_path):
        ret = backup_unix()
        assert ret == 0
        created_dirs = list(tmp_path.glob("Backup_Dev_*"))
        assert len(created_dirs) == 1
        assert (created_dirs[0] / "restore.sh").exists()
