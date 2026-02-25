# pis-utils

**Cross-platform Python Installation Support utilities for DTU**

A PyPI-ready package providing command-line tools for installing and configuring development tools at DTU (Technical University of Denmark).

## Features

- 🐍 **Miniforge3 Installer** - Automated conda/mamba installation from philipnickel/miniforge
- 🚀 **VS Code Installer** - Automated installation with extensions and settings
- 🔧 **Cross-platform** - Works on Windows, macOS (Intel & Apple Silicon), and Linux
- 📦 **Easy to use** - Simple CLI commands with beautiful progress indicators
- 🧪 **Well tested** - Comprehensive test suite with 40 tests
- 🛠️ **Clean Uninstall** - Complete removal of tools and user data

## Installation

### For End Users

**From GitHub (recommended for now):**
```bash
# Install VS Code with extensions and settings
uvx --from git+https://github.com/PN-CourseWork/miniforge-DTU-PIS pis-utils install vscode
```

**Future: From PyPI (once published):**
```bash
uvx pis-utils install vscode
```

### For Development

```bash
# Clone the repository
git clone https://github.com/PN-CourseWork/miniforge-DTU-PIS.git
cd PIS-Scripts-Utilities

# Install in editable mode with development dependencies
uv sync --all-extras

# Verify installation
pis-utils --version
```

## Usage

### Install Miniforge3 (Conda)

```bash
# Install latest stable release
pis-utils install conda

# Install development (prerelease) version
pis-utils install conda --prerelease
```

This will:
1. Download the appropriate Miniforge3 installer for your platform
2. Run the installer in batch mode with conda initialization
3. Set up conda/mamba for Python package management

**Note:** Restart your terminal after installation to activate conda.

### Install VS Code

```bash
# Install VS Code with extensions and settings
pis-utils install vscode
```

This will:
1. Download and install VS Code for your platform
2. Install Python development extensions (Python, Jupyter)
3. Apply settings to disable AI features and the Python Environments extension
4. Configure VS Code with optimal defaults for Python development

**Note:** The Python extension automatically installs Pylance and Python Debugger. The Python Environments extension is also installed but disabled via the `python.useEnvironmentsExtension` setting to maintain the classic environment selection experience.

### Uninstall Tools

```bash
# Uninstall conda/Miniforge3
pis-utils uninstall conda

# Uninstall VS Code
pis-utils uninstall vscode
```

### Available Commands

```bash
# Show help
pis-utils --help

# Show version
pis-utils --version

# Install commands
pis-utils install --help
pis-utils install conda
pis-utils install vscode

# Uninstall commands
pis-utils uninstall --help
pis-utils uninstall conda
pis-utils uninstall vscode
```

## Development

### Project Structure

```
PIS-Scripts-Utilities/
├── src/pis_utils/          # Main package
│   ├── cli.py              # CLI entry point
│   ├── config.toml         # Configuration (URLs, settings, extensions)
│   ├── core/               # Core utilities
│   │   ├── console.py      # Rich console instance
│   │   ├── platform.py     # Platform/architecture detection
│   │   └── download.py     # HTTP download utilities
│   └── commands/           # Command implementations
│       ├── install.py      # Install command group
│       ├── uninstall.py    # Uninstall command group
│       ├── conda.py        # Miniforge3 installer
│       └── vscode.py       # VS Code installer
├── tests/                  # Test suite
│   ├── commands/           # Command tests
│   ├── core/               # Utility tests
│   ├── conftest.py         # Pytest fixtures
│   └── test_cli.py         # CLI tests
├── pyproject.toml          # Package metadata
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/commands/test_vscode.py

# Run specific test function
pytest tests/commands/test_vscode.py::test_get_download_url_windows

# Run with coverage
pytest --cov --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Type check
mypy src/
```

### Building and Testing Locally

```bash
# Build the package
uv build

# Verify build outputs
ls dist/
# Should see: pis_utils-0.1.0-py3-none-any.whl and pis_utils-0.1.0.tar.gz

# Test installation from wheel
uv pip install dist/pis_utils-0.1.0-py3-none-any.whl --force-reinstall

# Test the CLI
pis-utils --version
pis-utils install vscode

# Test via uvx (simulates end-user experience)
uvx --from . pis-utils install vscode
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Maintainer

Philip Korsager Nickel - [philipnickel@outlook.dk](mailto:philipnickel@outlook.dk)

---

## Related Projects

This package is part of the DTU Miniforge3 ecosystem:

- **DTU Miniforge3** - Customized Miniforge3 installers for DTU courses
- **pis-utils** (this repo) - Python installation support utilities

### Legacy Installation Methods (from main DTU Miniforge3 repo)

For Miniforge3 and legacy VS Code installation scripts, see the [main DTU Miniforge3 repository](https://github.com/PN-CourseWork/miniforge-DTU-PIS).
