"""Tests for CLI functionality."""

from typer.testing import CliRunner

from pis_utils import __version__
from pis_utils.cli import app

runner = CliRunner()


def test_cli_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_help():
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Cross-platform Python installation support" in result.stdout


def test_cli_no_args():
    """Test CLI with no arguments shows help."""
    result = runner.invoke(app, [])
    # Typer returns exit code 2 when no args provided with no_args_is_help=True
    assert result.exit_code in (0, 2)
    assert "install" in result.stdout


def test_install_command_exists():
    """Test install command is registered."""
    result = runner.invoke(app, ["install", "--help"])
    assert result.exit_code == 0
    assert "Install various tools" in result.stdout


def test_install_vscode_command_exists():
    """Test install vscode subcommand exists."""
    result = runner.invoke(app, ["install", "vscode", "--help"])
    assert result.exit_code == 0
