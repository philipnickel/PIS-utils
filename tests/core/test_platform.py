"""Tests for platform detection utilities."""

from unittest.mock import patch

import pytest

from pis_utils.core import (
    Architecture,
    OperatingSystem,
    get_architecture,
    get_os,
    get_user_config_dir,
)


def test_get_os_windows(mock_platform_windows):
    """Test OS detection on Windows."""
    assert get_os() == OperatingSystem.WINDOWS


def test_get_os_macos(mock_platform_macos_intel):
    """Test OS detection on macOS."""
    assert get_os() == OperatingSystem.MACOS


def test_get_os_linux(mock_platform_linux):
    """Test OS detection on Linux."""
    assert get_os() == OperatingSystem.LINUX


def test_get_architecture_x86_64(mock_platform_windows):
    """Test architecture detection for x86_64."""
    assert get_architecture() == Architecture.X86_64


def test_get_architecture_arm64(mock_platform_macos_arm):
    """Test architecture detection for ARM64."""
    assert get_architecture() == Architecture.ARM64


def test_get_user_config_dir(tmp_path):
    """Test user config directory delegates to platformdirs."""
    with patch(
        "pis_utils.core.platform.platformdirs.user_config_dir",
        return_value=str(tmp_path / "TestApp"),
    ):
        result = get_user_config_dir("TestApp")
        assert result == tmp_path / "TestApp"


def test_get_os_unsupported(monkeypatch):
    """Test unsupported OS raises error."""
    monkeypatch.setattr("platform.system", lambda: "FreeBSD")
    with pytest.raises(OSError, match="Unsupported operating system"):
        get_os()


def test_get_architecture_unsupported(monkeypatch):
    """Test unsupported architecture raises error."""
    monkeypatch.setattr("platform.machine", lambda: "mips")
    with pytest.raises(OSError, match="Unsupported architecture"):
        get_architecture()
