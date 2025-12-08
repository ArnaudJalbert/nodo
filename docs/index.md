# Nodo

A minimalist CLI-based torrent download manager built with Clean Architecture principles.

## Overview

Nodo allows you to search for torrents via external aggregators and track downloaded files locally. It provides a simple command-line interface for managing your torrent downloads with support for multiple aggregator sources and integration with qBittorrent.

## Features

- 🔍 **Search torrents** from multiple aggregators (1337x, ThePirateBay, etc.)
- 📥 **Track and manage downloads** locally
- ⚙️ **Configure user preferences** (download paths, favorite sources)
- ⏸️ **Pause, resume, and remove** downloads
- 🔌 **Integration with qBittorrent**

## Quick Start

```bash
# Install with uv
uv sync

# Search for torrents
nodo search "ubuntu 24.04"

# Add a download
nodo add <magnet-link>

# List downloads
nodo list
```

## Architecture

Nodo follows **Clean Architecture** principles with four distinct layers:

- **Domain**: Entities, value objects, and business rules
- **Application**: Use cases and interfaces (ABCs)
- **Interface Adapters**: Repository and service implementations
- **Infrastructure**: CLI, dependency injection, configuration

This architecture ensures:
- ✅ Separation of concerns
- ✅ Testability
- ✅ Maintainability
- ✅ Independence from external frameworks

## Documentation

- [Getting Started](getting-started.md) - Installation and quick start guide
- [User Guide](user-guide/searching.md) - How to use Nodo
- [Architecture](architecture/overview.md) - Deep dive into the architecture
- [Development](development/setup.md) - Contributing and development setup

## Requirements

- Python 3.13+
- qBittorrent (for torrent client integration)

## License

MIT

