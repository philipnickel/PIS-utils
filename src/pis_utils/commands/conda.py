"""Miniforge/Conda installation and uninstallation."""

import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import typer

from pis_utils.config import config
from pis_utils.core import (
    OperatingSystem,
    console,
    download_file,
    get_os,
)

# ── Helper Functions ──────────────────────────────────────────────────────────


def get_installer_url(dev: bool = False) -> tuple[str, str]:
    """
    Get the download URL and filename for Miniforge installer.

    Uses uname-style naming: Miniforge3-{os}-{arch}.sh (or .exe on Windows).

    Args:
        dev: If True, use dev branch build

    Returns:
        Tuple of (download_url, filename)
    """
    repo = config["miniforge_github_repo"]
    if dev:
        base_url = (
            f"https://github.com/{repo}/releases/download/{config['miniforge_dev']}"
        )
    else:
        # GitHub's /releases/latest/download/ resolves to the newest release
        base_url = f"https://github.com/{repo}/releases/latest/download"

    if get_os() == OperatingSystem.WINDOWS:
        filename = "Miniforge3-Windows-x86_64.exe"
    else:
        # Raw uname values match Miniforge filenames exactly (e.g. aarch64, not arm64)
        filename = f"Miniforge3-{platform.uname().system}-{platform.uname().machine}.sh"

    return (f"{base_url}/{filename}", filename)


def get_conda_base_prefix() -> Path | None:
    """
    Get conda base installation directory by running 'conda info --base'.

    Returns:
        Path to conda base directory, or None if conda not found
    """
    try:
        result = subprocess.run(
            ["conda", "info", "--base"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            base_path = Path(result.stdout.strip())
            if base_path.exists():
                return base_path
    except FileNotFoundError:
        # conda command not found
        pass
    return None


def run_conda_init_reverse() -> bool:
    """
    Run 'conda init --reverse' to undo shell initialization.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Run with --dry-run first to show what will change
        console.print("  [dim]Running: conda init --reverse --dry-run[/dim]")
        subprocess.run(
            ["conda", "init", "--reverse", "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Actually run the reversal
        result = subprocess.run(
            ["conda", "init", "--reverse"],
            capture_output=True,
            text=True,
            check=False,
        )

        return result.returncode == 0
    except FileNotFoundError:
        # conda command not found
        return False


def is_safe_path(path: Path) -> bool:
    """
    Verify path is safe to delete (not root, home, or empty).

    Args:
        path: Path to check

    Returns:
        True if safe to delete, False otherwise
    """
    if not path:
        return False

    # Convert to absolute path for comparison
    path = path.resolve()

    # Dangerous paths to avoid
    dangerous_paths = [
        Path("/"),  # Root directory
        Path.home(),  # Home directory
    ]

    # Add Windows-specific dangerous paths
    if get_os() == OperatingSystem.WINDOWS:
        dangerous_paths.extend(
            [
                Path("C:\\"),
                Path("C:\\Windows"),
                Path("C:\\Program Files"),
                Path("C:\\Program Files (x86)"),
            ]
        )

    # Check if path matches any dangerous path
    for dangerous in dangerous_paths:
        if path == dangerous.resolve():
            return False

    # Check if path is too short (likely a system path)
    return len(str(path)) >= 5


# ── Install Command ───────────────────────────────────────────────────────────


def install(
    dev: bool = typer.Option(
        False,
        "--dev",
        help="Install development build from dev branch",
    ),
) -> None:
    """Install Miniforge3 (conda/mamba) with customizations."""
    try:
        os_type = get_os()
        uname = platform.uname()

        release_label = "dev" if dev else "latest"
        console.print(
            f"\n[bold]Installing Miniforge3[/bold] "
            f"([cyan]{uname.system}[/cyan], [cyan]{uname.machine}[/cyan], {release_label})\n"
        )

        # Download
        url, filename = get_installer_url(dev)
        with tempfile.TemporaryDirectory() as tmpdir:
            installer = Path(tmpdir) / filename
            download_file(url, installer)

            # Run installer (output shown directly)
            console.print("  Running installer…\n")
            if os_type == OperatingSystem.WINDOWS:
                result = subprocess.run([str(installer), "/S"])
            else:
                result = subprocess.run(["bash", str(installer), "-buc"])

            if result.returncode == 0:
                console.print("\n  [green]✓[/green] Installation complete")
            else:
                console.print("\n  [red]✗[/red] Installation failed")
                sys.exit(1)

        console.print(
            "\n[bold green]✓ All done![/bold green] "
            "Restart your terminal to activate conda."
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        sys.exit(1)


# ── Uninstall Command ─────────────────────────────────────────────────────────


def uninstall() -> None:
    """Uninstall Miniforge3/conda and remove all user data."""
    try:
        console.print("\n[bold]Uninstalling Miniforge3/Conda[/bold]\n")

        removed_something = False

        # Find conda
        base_prefix = get_conda_base_prefix()
        if not base_prefix:
            console.print("  [yellow]conda not found in PATH[/yellow]")
        else:
            console.print(f"  Found conda at: [cyan]{base_prefix}[/cyan]")

            if not is_safe_path(base_prefix):
                console.print(
                    f"  [red bold]ERROR:[/red bold] Refusing to delete unsafe path: {base_prefix}"
                )
                sys.exit(1)

        # Undo shell initialization
        if base_prefix:
            if run_conda_init_reverse():
                console.print("  [green]✓[/green] Shell initialization reversed")
            else:
                console.print(
                    "  [yellow]⚠[/yellow] Could not reverse conda init (may be okay)"
                )

        # Remove conda installation
        if base_prefix and base_prefix.exists():
            try:
                with console.status("  Removing conda installation…"):
                    shutil.rmtree(base_prefix)
                console.print("  [green]✓[/green] Conda installation removed")
                removed_something = True
            except PermissionError:
                console.print(
                    "  [red]✗[/red] Permission denied. Try running with administrator privileges."
                )
            except Exception as e:
                console.print(f"  [red]✗[/red] Failed to remove: {e}")
        elif not base_prefix:
            console.print("  [dim]No conda installation found[/dim]")

        # Remove user configuration
        condarc = Path.home() / ".condarc"
        conda_dir = Path.home() / ".conda"

        removed_items = []

        if condarc.exists():
            try:
                condarc.unlink()
                removed_items.append(".condarc")
                removed_something = True
            except Exception as e:
                console.print(f"  [red]✗[/red] Failed to remove .condarc: {e}")

        if conda_dir.exists():
            try:
                with console.status("  Removing .conda directory…"):
                    shutil.rmtree(conda_dir)
                removed_items.append(".conda")
                removed_something = True
            except Exception as e:
                console.print(f"  [red]✗[/red] Failed to remove .conda: {e}")

        if removed_items:
            console.print(f"  [green]✓[/green] Removed {', '.join(removed_items)}")

        if removed_something:
            console.print(
                "\n[bold green]✓ Uninstall complete![/bold green] "
                "Restart your terminal."
            )
        else:
            console.print("\n[yellow]No changes made – conda not found.[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        sys.exit(1)
