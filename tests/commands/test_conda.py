"""Tests for conda installation and uninstallation."""

from pathlib import Path
from unittest.mock import patch

from pis_utils.commands.conda import get_installer_url, is_safe_path
from pis_utils.core import OperatingSystem

# ── URL Generation Tests ─────────────────────────────────────────────────────


def _mock_uname(system: str, machine: str):
    """Create a mock uname result."""
    return type("uname_result", (), {"system": system, "machine": machine})()


def test_get_installer_url_windows():
    """Test Windows installer URL generation."""
    with patch("pis_utils.commands.conda.get_os", return_value=OperatingSystem.WINDOWS):
        url, filename = get_installer_url()
        assert (
            url
            == "https://github.com/philipnickel/miniforge/releases/download/latest/Miniforge3-Windows-x86_64.exe"
        )
        assert filename == "Miniforge3-Windows-x86_64.exe"


def test_get_installer_url_macos_intel():
    """Test macOS Intel installer URL generation."""
    with (
        patch("pis_utils.commands.conda.get_os", return_value=OperatingSystem.MACOS),
        patch(
            "pis_utils.commands.conda.platform.uname",
            return_value=_mock_uname("Darwin", "x86_64"),
        ),
    ):
        url, filename = get_installer_url()
        assert (
            url
            == "https://github.com/philipnickel/miniforge/releases/download/latest/Miniforge3-Darwin-x86_64.sh"
        )
        assert filename == "Miniforge3-Darwin-x86_64.sh"


def test_get_installer_url_macos_arm():
    """Test macOS ARM installer URL generation."""
    with (
        patch("pis_utils.commands.conda.get_os", return_value=OperatingSystem.MACOS),
        patch(
            "pis_utils.commands.conda.platform.uname",
            return_value=_mock_uname("Darwin", "arm64"),
        ),
    ):
        url, filename = get_installer_url()
        assert (
            url
            == "https://github.com/philipnickel/miniforge/releases/download/latest/Miniforge3-Darwin-arm64.sh"
        )
        assert filename == "Miniforge3-Darwin-arm64.sh"


def test_get_installer_url_linux_x86():
    """Test Linux x86_64 installer URL generation."""
    with (
        patch("pis_utils.commands.conda.get_os", return_value=OperatingSystem.LINUX),
        patch(
            "pis_utils.commands.conda.platform.uname",
            return_value=_mock_uname("Linux", "x86_64"),
        ),
    ):
        url, filename = get_installer_url()
        assert (
            url
            == "https://github.com/philipnickel/miniforge/releases/download/latest/Miniforge3-Linux-x86_64.sh"
        )
        assert filename == "Miniforge3-Linux-x86_64.sh"


def test_get_installer_url_linux_arm():
    """Test Linux ARM installer URL generation."""
    with (
        patch("pis_utils.commands.conda.get_os", return_value=OperatingSystem.LINUX),
        patch(
            "pis_utils.commands.conda.platform.uname",
            return_value=_mock_uname("Linux", "aarch64"),
        ),
    ):
        url, filename = get_installer_url()
        assert (
            url
            == "https://github.com/philipnickel/miniforge/releases/download/latest/Miniforge3-Linux-aarch64.sh"
        )
        assert filename == "Miniforge3-Linux-aarch64.sh"


def test_get_installer_url_dev():
    """Test dev build installer URL generation."""
    with (
        patch("pis_utils.commands.conda.get_os", return_value=OperatingSystem.LINUX),
        patch(
            "pis_utils.commands.conda.platform.uname",
            return_value=_mock_uname("Linux", "x86_64"),
        ),
    ):
        url, filename = get_installer_url(dev=True)
        assert (
            url
            == "https://github.com/philipnickel/miniforge/releases/download/dev/Miniforge3-Linux-x86_64.sh"
        )
        assert filename == "Miniforge3-Linux-x86_64.sh"


# ── Path Safety Tests ────────────────────────────────────────────────────────


def test_is_safe_path_valid():
    """Test safe path validation."""
    # Valid paths that should be safe to delete
    assert is_safe_path(Path("/home/user/miniforge3"))
    assert is_safe_path(Path("/opt/miniforge3"))
    assert is_safe_path(Path("/usr/local/miniforge3"))
    assert is_safe_path(Path.home() / "miniforge3")


def test_is_safe_path_dangerous():
    """Test unsafe path detection."""
    # Dangerous paths that should NOT be safe to delete
    assert not is_safe_path(Path("/"))
    assert not is_safe_path(Path.home())
    assert not is_safe_path(None)


def test_is_safe_path_windows():
    """Test Windows-specific unsafe paths."""
    with patch("pis_utils.commands.conda.get_os", return_value=OperatingSystem.WINDOWS):
        assert not is_safe_path(Path("C:\\"))
        assert not is_safe_path(Path("C:\\Windows"))
        assert not is_safe_path(Path("C:\\Program Files"))

        # But these should be safe
        assert is_safe_path(Path("C:\\Users\\testuser\\miniforge3"))
        assert is_safe_path(Path("C:\\ProgramData\\miniforge3"))
