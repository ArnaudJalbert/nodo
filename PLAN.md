# Nodo Implementation Plan

## Project Overview
Nodo is a CLI-based torrent download manager built with Clean Architecture principles. It allows users to search torrents, manage downloads, and configure preferences.

---

## Phase 1: Domain Layer
*No external dependencies - pure Python business logic*

### 1.1 Exceptions ✅
- [x] `DomainException` - Base exception
- [x] `ValidationError` - Input validation failures
- [x] `DownloadNotFoundError` - Download lookup failures
- [x] `DuplicateDownloadError` - Duplicate magnet link
- [x] `InvalidStateTransitionError` - Invalid status changes
- [x] `TorrentClientError` - Torrent client failures
- [x] `AggregatorError` - Aggregator search failures
- [x] `AggregatorTimeoutError` - Aggregator timeout
- [x] `FileSystemError` - File system operation failures

### 1.2 Value Objects ✅
- [x] `MagnetLink` - Magnet URI with validation
- [x] `FileSize` - File size with human-readable formatting
- [x] `AggregatorSource` - Torrent source/indexer name
- [x] `DownloadStatus` - Enum (DOWNLOADING, COMPLETED, FAILED, PAUSED)

### 1.3 Entities ✅
- [x] `TorrentSearchResult` - Ephemeral search result
- [x] `Download` - Core persisted entity
- [x] `UserPreferences` - Singleton preferences entity

---

## Phase 2: Application Layer
*Depends only on domain layer*

### 2.1 Interfaces (ABCs) ✅
- [x] `IDownloadRepository` - Download persistence
- [x] `IUserPreferencesRepository` - Preferences persistence
- [x] `IAggregatorService` - Torrent search service
- [x] `ITorrentClient` - Torrent client operations

### 2.2 Shared DTOs ✅
- [x] `DownloadDTO` - Download data transfer object
- [x] `TorrentSearchResultDTO` - Search result DTO
- [x] `UserPreferencesDTO` - Preferences DTO

### 2.3 User Preferences Use Cases
- [ ] `GetUserPreferences` - Load preferences
- [ ] `UpdateUserPreferences` - Update settings
- [ ] `AddFavoritePath` - Add favorite download location
- [ ] `RemoveFavoritePath` - Remove favorite location
- [ ] `AddFavoriteAggregator` - Add favorite source
- [ ] `RemoveFavoriteAggregator` - Remove favorite source

### 2.4 Download Management Use Cases
- [ ] `SearchTorrents` - Search across aggregators
- [ ] `AddDownload` - Add and start download
- [ ] `ListDownloads` - List downloads with filtering
- [ ] `GetDownloadStatus` - Get status and progress
- [ ] `RemoveDownload` - Remove download
- [ ] `PauseDownload` - Pause active download
- [ ] `ResumeDownload` - Resume paused download
- [ ] `RefreshDownloads` - Sync with torrent client

---

## Phase 3: Interface Adapters
*Implements domain interfaces*

### 3.1 Protocols
- [ ] `SQLAlchemySessionProtocol` - Database session protocol
- [ ] `QBittorrentClientProtocol` - qBittorrent API protocol

### 3.2 Repositories
- [ ] `SQLiteDownloadRepository` - SQLAlchemy implementation
- [ ] `SQLiteUserPreferencesRepository` - SQLAlchemy implementation

### 3.3 External Service Adapters
- [ ] `QBittorrentAdapter` - qBittorrent client adapter
- [ ] `AggregatorAdapter` - Base aggregator adapter
- [ ] Individual aggregator implementations (1337x, etc.)

---

## Phase 4: Infrastructure
*Framework and glue code*

### 4.1 Configuration
- [ ] Configuration management (TOML/YAML)
- [ ] Environment variable handling

### 4.2 Dependency Injection
- [ ] DI container setup
- [ ] Factory functions for adapters

### 4.3 CLI (Typer)
- [ ] `search` command - Search torrents
- [ ] `add` command - Add download
- [ ] `list` command - List downloads
- [ ] `status` command - Show download status
- [ ] `remove` command - Remove download
- [ ] `pause` command - Pause download
- [ ] `resume` command - Resume download
- [ ] `config` command - Manage preferences

### 4.4 Database
- [ ] SQLAlchemy models
- [ ] Database migrations (if needed)

---

## Phase 5: Documentation
*Built alongside implementation*

### 5.1 MkDocs Setup
- [ ] `mkdocs.yml` configuration
- [ ] `docs/index.md` - Overview
- [ ] `docs/getting-started.md` - Installation & Quick Start

### 5.2 Architecture Documentation
- [ ] `docs/architecture/overview.md`
- [ ] `docs/architecture/domain.md`
- [ ] `docs/architecture/application.md`
- [ ] `docs/architecture/interface-adapters.md`
- [ ] `docs/architecture/infrastructure.md`

### 5.3 User Guide
- [ ] `docs/user-guide/searching.md`
- [ ] `docs/user-guide/downloading.md`
- [ ] `docs/user-guide/preferences.md`

### 5.4 Other Documentation
- [ ] `CHANGELOG.md`
- [ ] `CONTRIBUTING.md`
- [ ] Update `README.md`

---

## Progress Log

| Date | Task | Status |
|------|------|--------|
| *TBD* | Project planning | Completed |
| 2025-12-08 | Phase 1.1 - Domain exceptions | Completed |
| 2025-12-08 | Phase 1.2 - Value objects | Completed |
| 2025-12-08 | Phase 1.3 - Entities | Completed |
| 2025-12-08 | Phase 2.2 - Shared DTOs | Completed |

---

## Notes
- All code requires 100% test coverage
- Run `ruff format .` and `ruff check .` before commits
- Run `pytest --cov=src --cov-fail-under=100` to verify coverage
- Follow Google-style docstrings
