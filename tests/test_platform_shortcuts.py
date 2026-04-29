"""Tests for Substr8 CLI v1.9.0 — Platform Shortcuts."""

import os
import subprocess
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

# Test imports
def test_platform_v2_cli_imports():
    """Test that all platform shortcut commands import correctly."""
    from substr8.platform_v2.cli import (
        doctor, bootstrap, up, down, restart,
        smoke, test_cmd, demo, clean,
    )
    assert doctor is not None
    assert bootstrap is not None
    assert up is not None
    assert down is not None
    assert restart is not None
    assert smoke is not None
    assert test_cmd is not None
    assert demo is not None
    assert clean is not None


def test_resolve_platform_root_missing():
    """Test that missing platform root gives helpful error (exit code 2)."""
    from substr8.platform_v2.cli import _resolve_platform_root
    with pytest.raises(SystemExit) as exc_info:
        _resolve_platform_root("/nonexistent/path/substr8-platform")
    assert exc_info.value.code == 2


def test_resolve_platform_root_env_override():
    """Test SUBSTR8_PLATFORM_ROOT environment variable override."""
    from substr8.platform_v2.cli import _resolve_platform_root
    # Create a temp dir with a Makefile
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        makefile = os.path.join(tmpdir, "Makefile")
        with open(makefile, "w") as f:
            f.write("test:\n\techo ok\n")

        os.environ["SUBSTR8_PLATFORM_ROOT"] = tmpdir
        try:
            result = _resolve_platform_root(None)
            assert result == tmpdir
        finally:
            del os.environ["SUBSTR8_PLATFORM_ROOT"]


def test_run_make_dry_run():
    """Test that dry-run prints command without executing."""
    from substr8.platform_v2.cli import _run_make
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        makefile = os.path.join(tmpdir, "Makefile")
        with open(makefile, "w") as f:
            f.write("test:\n\techo ok\n")

        # dry_run should return 0 and not actually run make
        code = _run_make(tmpdir, "test", dry_run=True)
        assert code == 0


def test_run_make_executes():
    """Test that _run_make actually runs make."""
    from substr8.platform_v2.cli import _run_make
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        makefile = os.path.join(tmpdir, "Makefile")
        with open(makefile, "w") as f:
            f.write("test:\n\t@echo ok\n")

        code = _run_make(tmpdir, "test")
        assert code == 0


def test_run_make_failure():
    """Test that make failure returns non-zero exit code."""
    from substr8.platform_v2.cli import _run_make
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        makefile = os.path.join(tmpdir, "Makefile")
        with open(makefile, "w") as f:
            f.write("test:\n\t@exit 1\n")

        code = _run_make(tmpdir, "test")
        assert code != 0


def test_doctor_command_missing_root():
    """Test that doctor command gives exit code 2 when platform root missing."""
    from substr8.platform_v2.cli import doctor
    runner = CliRunner()
    result = runner.invoke(doctor, ["--root", "/nonexistent"])
    assert result.exit_code == 2


def test_up_command_help():
    """Test that up command shows help with profile options."""
    from substr8.platform_v2.cli import up
    runner = CliRunner()
    result = runner.invoke(up, ["--help"])
    assert result.exit_code == 0
    assert "--profile" in result.output


def test_cli_top_level_shortcuts_registered():
    """Test that top-level shortcuts are registered in the main CLI."""
    from substr8.cli import main
    # Check that the shortcut commands exist
    assert "doctor" in main.commands
    assert "bootstrap" in main.commands
    assert "up" in main.commands
    assert "down" in main.commands
    assert "restart" in main.commands
    assert "smoke" in main.commands
    assert "test" in main.commands
    assert "demo" in main.commands
    assert "clean" in main.commands


def test_cli_help_shows_shortcuts():
    """Test that substr8 --help shows the shortcut commands."""
    from substr8.cli import main
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    # Top-level shortcuts should appear
    assert "doctor" in result.output
    assert "bootstrap" in result.output
    assert "smoke" in result.output