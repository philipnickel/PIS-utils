"""VS Code installation and configuration."""

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path

import typer

from pis_utils.config import config
from pis_utils.core import (
    OperatingSystem,
    console,
    download_file,
    get_architecture,
    get_os,
    get_user_config_dir,
)

# ── Configuration ─────────────────────────────────────────────────────────────


def load_vscode_install_config(config_path: Path | None = None) -> dict:
    """
    Load VS Code installation configuration (extensions and settings).

    Args:
        config_path: Path to custom config file. If None, uses built-in config.

    Returns:
        Dictionary with 'extensions' and 'settings' keys

    Raises:
        FileNotFoundError: If custom config file doesn't exist
        tomllib.TOMLDecodeError: If config file is invalid
    """
    if config_path is None:
        # Use built-in config
        return {
            "extensions": config["vscode_extensions"],
            "settings": config["vscode_settings"],
        }

    # Load custom config file
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "rb") as f:
        custom_config = tomllib.load(f)

    # Validate config structure - support both formats
    if "vscode" in custom_config and "install" in custom_config["vscode"]:
        # New format: [vscode.install.extensions] and [vscode.install.settings]
        install_config = custom_config["vscode"]["install"]
        if (
            "extensions" not in install_config
            or "list" not in install_config["extensions"]
        ):
            raise ValueError(
                "Config must contain [vscode.install.extensions] with 'list' key"
            )
        if "settings" not in install_config:
            raise ValueError("Config must contain [vscode.install.settings] section")

        return {
            "extensions": install_config["extensions"]["list"],
            "settings": install_config["settings"],
        }
    elif "extensions" in custom_config and "settings" in custom_config:
        # Old format: [extensions] and [settings] at top level (for custom configs)
        if "list" not in custom_config["extensions"]:
            raise ValueError("Config must contain [extensions] with 'list' key")

        return {
            "extensions": custom_config["extensions"]["list"],
            "settings": custom_config["settings"],
        }
    else:
        raise ValueError(
            "Config must contain either [vscode.install.extensions]/[vscode.install.settings] "
            "or [extensions]/[settings] sections"
        )


# ── Download URL Generation ───────────────────────────────────────────────────


def get_download_url() -> tuple[str, str]:
    """
    Return (url, filename) for the current platform.

    Returns:
        Tuple of (download_url, filename)

    Raises:
        OSError: If the platform is unsupported
    """
    os_type = get_os()
    base = config["vscode_download_base_url"]
    channel = config["vscode_stable_channel"]

    if os_type == OperatingSystem.WINDOWS:
        return (f"{base}/latest/win32-x64-user/{channel}", "vscode_installer.exe")
    elif os_type == OperatingSystem.MACOS:
        return (f"{base}/latest/darwin-universal/{channel}", "VSCode.zip")
    else:  # Linux
        return (f"{base}/latest/linux-x64/{channel}", "vscode.tar.gz")


# ── Installation ──────────────────────────────────────────────────────────────


def install_vscode_windows(installer: Path) -> None:
    """Install VS Code on Windows."""
    with console.status("  Running Windows installer (silent)…"):
        subprocess.run(
            [
                str(installer),
                "/VERYSILENT",
                "/MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath",
            ],
            check=True,
        )


def install_vscode_macos(installer: Path) -> None:
    """Install VS Code on macOS."""
    extract_dir = installer.parent / "vscode_extracted"
    extract_dir.mkdir(exist_ok=True)

    with (
        console.status("  Extracting VS Code for macOS…"),
        zipfile.ZipFile(installer) as zf,
    ):
        zf.extractall(extract_dir)

    app_src = extract_dir / "Visual Studio Code.app"
    app_dst = Path("/Applications/Visual Studio Code.app")

    if app_dst.exists():
        with console.status("  Removing existing installation…"):
            shutil.rmtree(app_dst)

    with console.status("  Moving app to /Applications…"):
        shutil.move(str(app_src), str(app_dst))


def install_vscode_linux(installer: Path) -> None:
    """Install VS Code on Linux."""
    install_dir = Path.home() / ".local" / "lib" / "vscode"
    install_dir.mkdir(parents=True, exist_ok=True)

    with (
        console.status("  Extracting VS Code for Linux…"),
        tarfile.open(installer, "r:gz") as tf,
    ):
        for member in tf.getmembers():
            # Strip top-level directory (equivalent to --strip-components=1)
            parts = Path(member.name).parts
            if len(parts) > 1:
                member.name = str(Path(*parts[1:]))
                tf.extract(member, install_dir, filter="data")

    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    symlink = bin_dir / "code"
    if symlink.exists() or symlink.is_symlink():
        symlink.unlink()

    symlink.symlink_to(install_dir / "bin" / "code")
    console.print(f"  Symlink created: [cyan]{symlink}[/cyan]")
    console.print("  [yellow]Make sure ~/.local/bin is in your PATH.[/yellow]")


def install_vscode_binary(installer: Path) -> None:
    """
    Install VS Code from the downloaded installer.

    Args:
        installer: Path to the downloaded installer file

    Raises:
        OSError: If the platform is unsupported
    """
    os_type = get_os()

    if os_type == OperatingSystem.WINDOWS:
        install_vscode_windows(installer)
    elif os_type == OperatingSystem.MACOS:
        install_vscode_macos(installer)
    else:  # Linux
        install_vscode_linux(installer)


# ── Find VS Code CLI ──────────────────────────────────────────────────────────


def find_code_cli() -> str:
    """
    Find the VS Code CLI executable.

    Returns:
        Path to the code CLI executable

    Raises:
        FileNotFoundError: If the code CLI cannot be found
    """
    if path := shutil.which("code"):
        return path

    os_type = get_os()

    if os_type == OperatingSystem.WINDOWS:
        candidates = [
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Programs"
            / "Microsoft VS Code"
            / "bin"
            / "code.cmd",
            Path(os.environ.get("PROGRAMFILES", ""))
            / "Microsoft VS Code"
            / "bin"
            / "code.cmd",
        ]
        for c in candidates:
            if c.exists():
                return str(c)

    raise FileNotFoundError(
        "Could not find the `code` CLI. "
        "On Windows, try opening a new terminal after installation. "
        "On Linux, make sure ~/.local/bin is in your PATH."
    )


# ── Extensions ────────────────────────────────────────────────────────────────


def install_extensions_list(code_cli: str, extensions: list[str]) -> None:
    """
    Install VS Code extensions.

    Args:
        code_cli: Path to the code CLI executable
        extensions: List of extension IDs to install
    """
    total = len(extensions)
    for i, ext in enumerate(extensions, 1):
        with console.status(f"  [{i}/{total}] Installing [cyan]{ext}[/cyan]…"):
            result = subprocess.run(
                [code_cli, "--install-extension", ext, "--force"],
                capture_output=True,
                text=True,
            )
        if result.returncode == 0:
            console.print(f"  [{i}/{total}] [green]✓[/green] {ext}")
        else:
            console.print(
                f"  [{i}/{total}] [red]✗[/red] {ext} — {result.stderr.strip()}"
            )


# ── Settings ──────────────────────────────────────────────────────────────────


def get_settings_path() -> Path:
    """Get the path to VS Code's settings.json file."""
    return get_user_config_dir("Code") / "User" / "settings.json"


def apply_settings_dict(settings: dict[str, object]) -> None:
    """
    Apply VS Code settings.

    Args:
        settings: Dictionary of settings to apply
    """
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, object] = {}
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            console.print(
                "  [yellow]Warning: existing settings.json is invalid – overwriting.[/yellow]"
            )

    merged = {**existing, **settings}
    settings_path.write_text(json.dumps(merged, indent=4), encoding="utf-8")
    console.print(f"  [green]✓[/green] Settings applied ({len(settings)} settings)")


# ── Main Install Command ──────────────────────────────────────────────────────


def install(
    config_path: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to custom config file (default: built-in config.toml)",
        exists=True,
        dir_okay=False,
    ),
) -> None:
    """Install VS Code with extensions and settings from config file."""
    try:
        os_type = get_os()
        arch = get_architecture()

        # Load configuration
        try:
            vscode_config = load_vscode_install_config(config_path)
            extensions = vscode_config["extensions"]
            settings = vscode_config["settings"]

            if config_path:
                console.print(f"  [dim]Using config: {config_path}[/dim]")
            else:
                console.print("  [dim]Using default config[/dim]")
        except Exception as e:
            console.print(f"[red bold]Config Error:[/red bold] {e}")
            sys.exit(1)

        console.print(
            f"\n[bold]Installing VS Code[/bold] "
            f"([cyan]{os_type.value}[/cyan], [cyan]{arch.value}[/cyan])\n"
        )

        # Download & install
        if shutil.which("code"):
            console.print("  [green]✓[/green] VS Code already installed")
        else:
            url, filename = get_download_url()
            with tempfile.TemporaryDirectory() as tmpdir:
                installer = Path(tmpdir) / filename
                download_file(url, installer)
                install_vscode_binary(installer)
            console.print("  [green]✓[/green] VS Code installed")

        # Extensions
        try:
            code_cli = find_code_cli()
            install_extensions_list(code_cli, extensions)
        except FileNotFoundError as e:
            console.print(f"  [red]✗[/red] {e}")

        # Settings
        apply_settings_dict(settings)

        console.print(
            "\n[bold green]✓ All done![/bold green] "
            "Restart your terminal if [cyan]code[/cyan] is not yet on your PATH."
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        sys.exit(1)


# ── Uninstall Command ─────────────────────────────────────────────────────────


def uninstall() -> None:
    """Uninstall VS Code and remove all user data (clean uninstall)."""
    try:
        os_type = get_os()

        console.print("\n[bold]Uninstalling VS Code[/bold]\n")

        app_removed = False

        # Remove application
        if os_type == OperatingSystem.MACOS:
            app_path = Path("/Applications/Visual Studio Code.app")
            if app_path.exists():
                with console.status("  Removing VS Code.app…"):
                    shutil.rmtree(app_path)
                console.print("  [green]✓[/green] Application removed")
                app_removed = True
            else:
                console.print("  [yellow]VS Code not found at /Applications[/yellow]")

        elif os_type == OperatingSystem.LINUX:
            install_dir = Path.home() / ".local" / "lib" / "vscode"
            symlink = Path.home() / ".local" / "bin" / "code"

            if install_dir.exists():
                with console.status("  Removing VS Code…"):
                    shutil.rmtree(install_dir)
                console.print("  [green]✓[/green] VS Code removed")
                app_removed = True

            if symlink.exists() or symlink.is_symlink():
                symlink.unlink()
                console.print("  [green]✓[/green] Symlink removed")
                app_removed = True

            if not app_removed:
                console.print("  [yellow]VS Code not found[/yellow]")
                console.print(
                    "  [dim]If installed via package manager: sudo apt-get remove code[/dim]"
                )

        elif os_type == OperatingSystem.WINDOWS:
            console.print(
                "  [yellow]On Windows, uninstall via Settings → Apps → Apps & features[/yellow]"
            )
            local_app = (
                Path(os.environ.get("LOCALAPPDATA", ""))
                / "Programs"
                / "Microsoft VS Code"
            )
            program_files = (
                Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft VS Code"
            )

            if local_app.exists():
                console.print(f"  [dim]Found at: {local_app}[/dim]")
            elif program_files.exists():
                console.print(f"  [dim]Found at: {program_files}[/dim]")

        # Remove user data
        config_dir = get_user_config_dir("Code")
        vscode_dir = Path.home() / ".vscode"

        removed_items = []

        if config_dir.exists():
            with console.status("  Removing settings and extensions…"):
                shutil.rmtree(config_dir)
            removed_items.append("settings & extensions")

        if vscode_dir.exists():
            with console.status("  Removing user data…"):
                shutil.rmtree(vscode_dir)
            removed_items.append("user data")

        if removed_items:
            console.print(f"  [green]✓[/green] Removed {', '.join(removed_items)}")
        else:
            console.print("  [yellow]No user data found[/yellow]")

        if app_removed or removed_items:
            console.print("\n[bold green]✓ Uninstall complete![/bold green]")
        else:
            console.print("\n[yellow]No changes made – VS Code not found.[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red bold]Error:[/red bold] {e}")
        sys.exit(1)
