"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def mock_platform_windows(monkeypatch):
    """Mock platform detection for Windows."""
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")


@pytest.fixture
def mock_platform_macos_intel(monkeypatch):
    """Mock platform detection for macOS Intel."""
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")


@pytest.fixture
def mock_platform_macos_arm(monkeypatch):
    """Mock platform detection for macOS Apple Silicon."""
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")


@pytest.fixture
def mock_platform_linux(monkeypatch):
    """Mock platform detection for Linux."""
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
