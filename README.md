# Nodo

A minimalist CLI-based torrent download manager built with Clean Architecture principles. Search for torrents via external aggregators and track downloaded files locally.

## Features

- Search torrents from multiple aggregators (1337x, ThePirateBay, etc.)
- Track and manage downloads locally
- Configure user preferences (download paths, favorite sources)
- Pause, resume, and remove downloads
- Integration with qBittorrent

## Installation

Requires Python 3.13+

```bash
# Clone the repository
git clone https://github.com/username/nodo.git
cd nodo

# Install with uv
uv sync

# Or install with pip
pip install -e .
```

## Usage

```bash
# Search for torrents
nodo search "ubuntu 24.04"

# Add a download
nodo add <magnet-link>

# List downloads
nodo list

# Check download status
nodo status <download-id>

# Pause/resume downloads
nodo pause <download-id>
nodo resume <download-id>

# Configure preferences
nodo config --download-path ~/Downloads
```

## Configuration

Nodo stores configuration in `~/.config/nodo/config.toml`. Default settings:

- **Download path**: `~/Downloads`
- **Max concurrent downloads**: 3
- **Auto-start downloads**: enabled

## Development

### Setup

```bash
# Clone and install dev dependencies
git clone https://github.com/username/nodo.git
cd nodo
uv sync --dev
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

### Pre-commit Checklist

```bash
uv run ruff format .
uv run ruff check .
uv run pytest --cov=src
uv lock
```

## Architecture

Nodo follows Clean Architecture with four layers:

- **Domain**: Entities, value objects, and business rules
- **Application**: Use cases and interfaces (ABCs)
- **Interface Adapters**: Repository and service implementations
- **Infrastructure**: CLI, dependency injection, configuration

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
