"""Tests for VS Code installation command."""

import json
from unittest.mock import Mock, patch

from pis_utils.commands.vscode import (
    apply_settings_dict,
    get_download_url,
    get_settings_path,
    install_extensions_list,
)


def test_get_download_url_windows(mock_platform_windows):
    """Test download URL generation for Windows."""
    url, filename = get_download_url()
    assert "win32-x64-user" in url
    assert filename == "vscode_installer.exe"


def test_get_download_url_macos(mock_platform_macos_arm):
    """Test download URL generation for macOS (universal binary)."""
    url, filename = get_download_url()
    assert "darwin-universal" in url
    assert filename == "VSCode.zip"


def test_get_download_url_linux(mock_platform_linux):
    """Test download URL generation for Linux."""
    url, filename = get_download_url()
    assert "linux-x64" in url
    assert filename == "vscode.tar.gz"


def test_get_settings_path(tmp_path):
    """Test settings path delegates to platformdirs."""
    with patch(
        "pis_utils.core.platform.platformdirs.user_config_dir",
        return_value=str(tmp_path / "Code"),
    ):
        path = get_settings_path()
        assert path == tmp_path / "Code" / "User" / "settings.json"


def test_apply_settings_dict_new_file(tmp_path, monkeypatch):
    """Test applying settings to a new file."""
    settings_file = tmp_path / "settings.json"

    def mock_get_settings_path():
        return settings_file

    monkeypatch.setattr(
        "pis_utils.commands.vscode.get_settings_path", mock_get_settings_path
    )

    test_settings = {
        "editor.fontSize": 16,
        "editor.tabSize": 2,
    }

    with patch("pis_utils.commands.vscode.console"):
        apply_settings_dict(test_settings)

    assert settings_file.exists()
    written_settings = json.loads(settings_file.read_text())
    assert written_settings["editor.fontSize"] == 16
    assert written_settings["editor.tabSize"] == 2


def test_apply_settings_dict_merge_existing(tmp_path, monkeypatch):
    """Test merging settings with existing file."""
    settings_file = tmp_path / "settings.json"
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    # Create existing settings
    existing = {
        "editor.fontSize": 12,
        "files.autoSave": "off",
    }
    settings_file.write_text(json.dumps(existing))

    def mock_get_settings_path():
        return settings_file

    monkeypatch.setattr(
        "pis_utils.commands.vscode.get_settings_path", mock_get_settings_path
    )

    new_settings = {
        "editor.fontSize": 16,  # Should override
        "editor.tabSize": 4,  # Should add
    }

    with patch("pis_utils.commands.vscode.console"):
        apply_settings_dict(new_settings)

    written_settings = json.loads(settings_file.read_text())
    assert written_settings["editor.fontSize"] == 16  # Overridden
    assert written_settings["editor.tabSize"] == 4  # Added
    assert written_settings["files.autoSave"] == "off"  # Preserved


def test_apply_settings_dict_invalid_json(tmp_path, monkeypatch):
    """Test handling of invalid existing JSON."""
    settings_file = tmp_path / "settings.json"
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text("invalid json {")

    def mock_get_settings_path():
        return settings_file

    monkeypatch.setattr(
        "pis_utils.commands.vscode.get_settings_path", mock_get_settings_path
    )

    new_settings = {"editor.fontSize": 14}

    with patch("pis_utils.commands.vscode.console"):
        apply_settings_dict(new_settings)

    # Should overwrite invalid JSON
    written_settings = json.loads(settings_file.read_text())
    assert written_settings["editor.fontSize"] == 14


def test_install_extensions_list_success():
    """Test successful extension installation."""
    mock_result = Mock()
    mock_result.returncode = 0

    with (
        patch("subprocess.run", return_value=mock_result),
        patch("pis_utils.commands.vscode.console"),
    ):
        install_extensions_list("code", ["ext1", "ext2"])


def test_install_extensions_list_failure():
    """Test extension installation failure."""
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stderr = "Error message"

    with (
        patch("subprocess.run", return_value=mock_result),
        patch("pis_utils.commands.vscode.console"),
    ):
        install_extensions_list("code", ["failing-ext"])
