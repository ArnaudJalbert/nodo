# Technology Stack

## Core Technologies

- **Language:** Python 3.13+
- **Package Manager:** UV (fast, modern)
- **Database:** SQLite (file-based) - *To be implemented*
- **ORM:** SQLAlchemy 2.0+ - *To be implemented*
- **Torrent Client:** qBittorrent with `qbittorrent-api` - *To be implemented*
- **Torrent Search:** `torrent-search-python` - *To be implemented*
- **CLI Framework:** Typer - *To be implemented*
- **Terminal UI:** Rich (tables, progress bars, formatting) - *To be implemented*
- **Validation:** Pydantic (Request/Response models) - *To be implemented*

---

## Dependencies

### Production

**Current Status:** No production dependencies yet (project in early development phase)

```toml
[project]
name = "nodo"
version = "0.3.0"
description = "Minimalist torrent download manager"
requires-python = ">=3.13"
dependencies = []  # To be added as features are implemented
```

**Planned Dependencies:**
- `typer>=0.12.0` - CLI framework
- `rich>=13.7.0` - Terminal UI
- `sqlalchemy>=2.0` - ORM
- `qbittorrent-api>=2024.1` - qBittorrent client
- `torrent-search-python>=1.0` - Torrent search
- `requests>=2.31.0` - HTTP client
- `pydantic>=2.0` - Validation

### Development

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "pytest-cov>=7.0.0",
    "ruff>=0.14.8",
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.5.0",
    "mkdocstrings[python]>=0.24.0",
]
```

**Note:** MyPy is not currently included but can be added if needed.

---

## Installation with UV

### Setup

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone project
git clone https://github.com/username/nodo.git
cd nodo

# Install dependencies (including dev)
uv sync --dev

# Or install only dev dependencies
uv sync
```

### Running

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Run documentation server
uv run nodo-docs
# Or: uv run python -m nodo.infrastructure.documentation.main

# CLI application (to be implemented)
# uv run python -m nodo.infrastructure.cli.main
# nodo search ubuntu
```

---

## Quick Start Commands

### Development

```bash
# Format code
ruff format .

# Lint with auto-fix
ruff check --fix .

# Run tests with coverage
pytest --cov=src --cov-fail-under=100

# Type checking (optional)
mypy src/
```

### Documentation

```bash
# Serve docs locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Application

**Status:** CLI commands to be implemented

```bash
# Planned commands:
# nodo search "ubuntu"
# nodo add <magnet_link>
# nodo list
# nodo status <download_id>
# nodo pause <download_id>
# nodo resume <download_id>
# nodo remove <download_id>
# nodo config --download-path ~/Downloads
```

---

## Configuration

### Config File Location

`~/.config/nodo/config.toml` (to be implemented)

### Config File Format

```toml
[database]
path = "~/.torrent-cli/downloads.db"

[qbittorrent]
host = "localhost"
port = 8080
username = "admin"
password = "adminpass"

[downloads]
directory = "~/Downloads"
```

### Environment Variables (Alternative)

```bash
TORRENT_CLI_DB_PATH=/path/to/downloads.db
QBT_HOST=localhost
QBT_PORT=8080
QBT_USERNAME=admin
QBT_PASSWORD=adminpass
TORRENT_CLI_DOWNLOAD_DIR=/path/to/downloads
```

### First-Time Setup

**Status:** To be implemented

```bash
# Planned: Create default config file
# nodo init

# Edit configuration
# nano ~/.config/nodo/config.toml
```

---

## External Services

### qBittorrent

**Required:** qBittorrent must be running and accessible.

**Installation:**
```bash
# Linux
sudo apt install qbittorrent-nox

# macOS
brew install qbittorrent

# Run headless
qbittorrent-nox
```

**Web UI:**
- Default: http://localhost:8080
- Username: admin
- Password: adminpass (change in settings)

### Torrent Search Aggregators

**Supported sources:**
- 1337x
- ThePirateBay
- RARBG
- Nyaa
- TorrentGalaxy
- LimeTorrents

**No setup required** - accessed via `torrent-search-python` library.

---

## Database

### SQLite

**Status:** To be implemented

**Planned Location:** `~/.config/nodo/downloads.db`

**Schema managed by:** SQLAlchemy migrations (Alembic) - *To be implemented*

**Planned Tables:**
- `downloads` - Download entities
- `user_preferences` - Singleton preferences

**Advantages:**
- No server required
- File-based (easy backup)
- Zero configuration
- Cross-platform

---

## CLI Framework: Typer

**Why Typer:**
- Built on Click
- Automatic help generation
- Type hints for arguments
- Easy command grouping
- Excellent error messages

**Example:**
```python
import typer

app = typer.Typer()

@app.command()
def search(
    query: str,
    max_results: int = typer.Option(10, help="Max results")
):
    """Search for torrents"""
    ...
```

---

## Terminal UI: Rich

**Features:**
- Tables
- Progress bars
- Syntax highlighting
- Markdown rendering
- Colors and styling

**Example:**
```python
from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Downloads")
table.add_column("Title", style="cyan")
table.add_column("Status", style="green")

for download in downloads:
    table.add_row(download.title, download.status)

console.print(table)
```

---

## Development Tools

### Ruff

**Purpose:** Fast Python linter and formatter

**Usage:**
```bash
ruff format .
ruff check --fix .
```

### Pytest

**Purpose:** Testing framework

**Usage:**
```bash
pytest --cov=src --cov-fail-under=100
```

### MkDocs

**Purpose:** Documentation site generator

**Usage:**
```bash
mkdocs serve
mkdocs build
```

### MyPy (Optional)

**Purpose:** Static type checker

**Usage:**
```bash
mypy src/
```

---

## Project Structure

```
nodo/
├── src/
│   └── nodo/
│       ├── domain/
│       ├── application/
│       ├── interface_adapters/  # (to be implemented)
│       └── infrastructure/       # (minimal - only documentation)
├── tests/
├── docs/
├── pyproject.toml
├── README.md
└── .gitignore
```

---

## Python Version

**Minimum:** Python 3.13

**Why 3.13+:**
- Modern type hints (`list[str]`, `dict[str, int]`)
- `tomllib` for TOML parsing (standard library)
- Performance improvements
- Better error messages
- Latest language features

---

## Package Management: UV

**Why UV:**
- Faster than pip/poetry
- Modern dependency resolution
- Virtual environment management
- Compatible with pip
- Lock file support

**Key Commands:**
```bash
uv add <package>           # Add dependency
uv add --dev <package>     # Add dev dependency
uv remove <package>        # Remove dependency
uv sync                    # Install all dependencies
uv run <command>           # Run in virtual environment
```

---

## Summary

**Core Stack:**
- Python 3.13+, UV
- SQLite, SQLAlchemy - *To be implemented*
- qBittorrent, torrent-search-python - *To be implemented*
- Typer, Rich, Pydantic - *To be implemented*

**Development:**
- Ruff (format/lint), Pytest (test), MkDocs (docs)
- Optional: MyPy (type check)

**Current Status:**
- Domain layer: ✅ Complete
- Application layer: ✅ Use cases implemented
- Interface Adapters: ⏳ To be implemented
- Infrastructure: ⏳ Minimal (documentation only)

**External Dependencies:** qBittorrent (must be running) - *When implemented*
