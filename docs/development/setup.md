# Development Setup

This guide will help you set up a development environment for Nodo.

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git
- qBittorrent (for testing torrent client integration)

## Clone the Repository

```bash
git clone https://github.com/username/nodo.git
cd nodo
```

## Install Dependencies

### With uv (Recommended)

```bash
# Install all dependencies including dev dependencies
uv sync --dev
```

### With pip

```bash
# Install in development mode
pip install -e ".[dev]"
```

## Development Dependencies

The project includes the following development tools:

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **ruff** - Linting and formatting

## Project Structure

```
nodo/
├── src/nodo/              # Source code
│   ├── domain/            # Domain layer
│   ├── application/       # Application layer
│   ├── interface_adapters/ # Interface adapters
│   └── infrastructure/    # Infrastructure layer
├── tests/                 # Test suite
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
└── mkdocs.yml            # Documentation configuration
```

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run with Coverage

```bash
uv run pytest --cov=src --cov-report=term
```

### Run Specific Test File

```bash
uv run pytest tests/nodo/domain/entities/test_download.py
```

### Run Specific Test

```bash
uv run pytest tests/nodo/domain/entities/test_download.py::test_download_creation
```

## Code Quality

### Format Code

```bash
uv run ruff format .
```

### Lint Code

```bash
uv run ruff check .
```

### Fix Linting Issues

```bash
uv run ruff check --fix .
```

## Pre-commit Checklist

Before committing, ensure:

1. ✅ Code is formatted: `uv run ruff format .`
2. ✅ No linting errors: `uv run ruff check .`
3. ✅ All tests pass: `uv run pytest`
4. ✅ Coverage is 100%: `uv run pytest --cov=src --cov-fail-under=100`
5. ✅ Dependencies are locked: `uv lock`

## Running Documentation Locally

### Start MkDocs Server

```bash
uv run mkdocs serve
```

Documentation will be available at `http://127.0.0.1:8000`

### Build Documentation

```bash
uv run mkdocs build
```

This creates a `site/` directory with static HTML files.

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Ruff
- Pytest

### PyCharm

Configure:
- Python interpreter: Use the virtual environment created by uv
- Test runner: pytest
- Code style: Follow PEP 8 (enforced by ruff)

## Debugging

### Run with Debugger

```bash
# Using Python debugger
python -m pdb -m pytest tests/...

# Using VS Code
# Set breakpoints and use the debugger
```

### Enable Logging

Set log level via environment variable:

```bash
export NODO_LOG_LEVEL=DEBUG
```

## Next Steps

- [Testing](testing.md) - Learn about the testing strategy
- [Contributing](contributing.md) - Guidelines for contributing

