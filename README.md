# pis-utils

Cross-platform CLI for installing and configuring VS Code and Miniforge3 at DTU.

## Install

```bash
uvx pis-utils install vscode
uvx pis-utils install conda
```

Or install the tool itself:

```bash
uv tool install pis-utils
```

## Usage

```bash
# Install VS Code with extensions and settings
pis-utils install vscode

# Install Miniforge3 (conda/mamba)
pis-utils install conda

# Install dev build of Miniforge3
pis-utils install conda --dev

# Use a custom config for VS Code
pis-utils install vscode --config path/to/config.toml

# Uninstall
pis-utils uninstall vscode
pis-utils uninstall conda
```

## What it does

**VS Code** - Downloads and installs VS Code, installs extensions (Python, Jupyter), applies settings (disables AI features, disables Python Environments extension).

**Miniforge3** - Downloads and runs the Miniforge3 installer for your platform in batch mode.

Both commands detect your OS and architecture automatically. Supports Windows, macOS (Intel and Apple Silicon), and Linux.

## Development

```bash
git clone https://github.com/philipnickel/PIS-utils.git
cd PIS-utils
uv sync --all-extras
pytest
```

## License

MIT
