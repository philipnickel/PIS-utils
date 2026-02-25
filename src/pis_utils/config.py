"""Configuration management for pis-utils."""

import tomllib
from pathlib import Path

# Load config once at module import
_config_path = Path(__file__).parent / "config.toml"
with open(_config_path, "rb") as f:
    config = tomllib.load(f)
