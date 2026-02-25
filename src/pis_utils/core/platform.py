"""Platform detection utilities."""

import platform
from enum import StrEnum
from pathlib import Path

import platformdirs


class OperatingSystem(StrEnum):
    """Supported operating systems."""

    WINDOWS = "Windows"
    MACOS = "Darwin"
    LINUX = "Linux"


class Architecture(StrEnum):
    """Supported architectures."""

    X86_64 = "x86_64"
    ARM64 = "arm64"


def get_os() -> OperatingSystem:
    """
    Get the current operating system.

    Returns:
        OperatingSystem enum value

    Raises:
        OSError: If the operating system is not supported
    """
    system = platform.system()
    try:
        return OperatingSystem(system)
    except ValueError:
        raise OSError(f"Unsupported operating system: {system}") from None


def get_architecture() -> Architecture:
    """
    Get the current CPU architecture.

    Returns:
        Architecture enum value

    Raises:
        OSError: If the architecture is not supported
    """
    machine = platform.machine().lower()
    # Normalize architecture names
    if machine in ("amd64", "x86_64"):
        return Architecture.X86_64
    elif machine in ("arm64", "aarch64"):
        return Architecture.ARM64
    else:
        raise OSError(f"Unsupported architecture: {machine}")


def get_user_config_dir(app_name: str) -> Path:
    """Get the user configuration directory for an application."""
    return Path(platformdirs.user_config_dir(app_name))


__all__ = [
    "OperatingSystem",
    "Architecture",
    "get_os",
    "get_architecture",
    "get_user_config_dir",
]
