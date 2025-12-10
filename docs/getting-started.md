# Getting Started

This guide will help you get started with Nodo.

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- qBittorrent (for torrent client integration)

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/username/nodo.git
cd nodo

# Install with uv
uv sync
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/username/nodo.git
cd nodo

# Install with pip
pip install -e .
```

## Configuration

Nodo stores configuration in `~/.config/nodo/config.toml`. The default settings are:

- **Download path**: `~/Downloads`
- **Max concurrent downloads**: 3
- **Auto-start downloads**: enabled

You can configure these settings using the CLI:

```bash
# Set download path
nodo config --download-path ~/Downloads

# Set max concurrent downloads
nodo config --max-concurrent 5
```

## Basic Usage

### Search for Torrents

Search across multiple aggregators:

```bash
nodo search "ubuntu 24.04"
```

This will search for torrents matching your query and display results from all configured aggregators.

### Add a Download

Add a torrent using a magnet link:

```bash
nodo add magnet:?xt=urn:btih:...
```

The download will start automatically if auto-start is enabled.

### List Downloads

View all your downloads:

```bash
# List all downloads
nodo list

# List only active downloads
nodo list --status downloading

# List completed downloads
nodo list --status completed
```

### Check Download Status

Get detailed information about a specific download:

```bash
nodo status <download-id>
```

### Pause and Resume

Control your downloads:

```bash
# Pause a download
nodo pause <download-id>

# Resume a paused download
nodo resume <download-id>
```

### Remove a Download

Remove a download from tracking:

```bash
# Remove from tracking only
nodo remove <download-id>

# Remove and delete files
nodo remove <download-id> --delete-files
```

## Next Steps

- Read the [User Guide](user-guide/coming_soon.md) for detailed usage instructions
- Explore the [Architecture](architecture/overview.md) to understand how Nodo works
- Check out the [Development Guide](development/setup.md) if you want to contribute

