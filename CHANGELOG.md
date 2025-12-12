# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-12-11

### Changed

- **BREAKING:** Renamed `MagnetLink` to `TorrentLink` to reflect support for multiple URL formats
  - Now accepts magnet:, http:, and https: URL schemes
  - `info_hash` property now returns `str | None` (None for non-magnet URLs)
  - Equality comparison falls back to full URI comparison when info_hash unavailable
  - Backward compatibility: `MagnetLink` is now an alias for `TorrentLink`

### Added

- Support for HTTP/HTTPS torrent file URLs in addition to magnet links
- Better Prowlarr integration - no longer skips results with HTTP URLs in guid field
- Prowlarr indexer manager integration
  - `ProwlarrIndexerManager` - Concrete implementation of `IndexerManager` for Prowlarr API
  - `IProwlarrSource` - Protocol defining raw Prowlarr API boundary in interface adapters layer
  - `ProwlarrAdapter` - Infrastructure layer HTTP client for Prowlarr API
- Comprehensive indexer manager architecture with clean separation of concerns
  - Infrastructure layer returns raw data (dicts)
  - Interface adapters handle mapping to domain entities
  - Application layer works with abstract `IndexerManager` interface

### Changed

- **Architecture Refactoring** - Complete migration from aggregator pattern to indexer manager pattern
  - Replaced `IAggregatorService` and `IAggregatorServiceRegistry` with generic `IndexerManager` ABC
  - Replaced `AggregatorSource` with `IndexerSource` value object
  - Renamed `AggregatorError` and `AggregatorTimeoutError` to `IndexerError` and `IndexerTimeoutError`
  - Updated `SearchTorrents` use case to use `IndexerManager` instead of aggregator registry
  - Renamed `UserPreferences.favorite_aggregators` to `UserPreferences.favorite_indexers`
- **IndexerSource Value Object** - Now only supports Prowlarr
  - Reduced supported indexers list to Prowlarr only (future-proof for adding more)
  - Updated validation and canonical name handling
- **Documentation** - Complete update to reflect new architecture
  - Updated architecture overview with new indexer manager pattern
  - Updated domain layer documentation with IndexerSource details
  - Updated application layer documentation with IndexerManager ABC
  - Rewrote interface adapters documentation with Prowlarr specifics
  - Updated infrastructure documentation

### Fixed

- Test coverage - Updated all tests to use Prowlarr as the only supported indexer
  - Updated 292 tests across all layers
  - Maintained 100% code coverage throughout refactoring

## [0.4.0] - 2025-12-08

### Added

- Download management use cases (Phase 2.4 completion)
  - `RemoveDownload` - Remove download from tracking with optional file deletion
  - `PauseDownload` - Pause an active download
  - `ResumeDownload` - Resume a paused download
  - `RefreshDownloads` - Sync download statuses with a torrent client
- Comprehensive test suites for all new use cases with 100% coverage
- Error handling for invalid state transitions (pause/resume)
- Graceful error handling in RefreshDownloads (continues processing on individual failures)

### Changed

- `AddDownload` now sets download status to FAILED when a torrent client fails
  - Improves error tracking by persisting the failure state
  - Download entity is saved with FAILED status before the exception is raised
- `AddFavoriteAggregator` now validates aggregator is supported
  - Raises `ValidationError` for unsupported aggregators
  - Provides a helpful error message with a list of supported aggregators

## [0.3.0] - 2025-12-08

### Added

- Application layer data transfer objects (DTOs)
  - `DownloadDTO` - Data transfer object for Download entity
  - `TorrentSearchResultDTO` - Data transfer object for TorrentSearchResult entity
- Test suite for application layer DTOs
  - Comprehensive tests for all DTOs with 100% coverage
  - Tests for immutability, equality, and edge cases
- Documentation infrastructure with MkDocs
  - Complete MkDocs setup with Material theme
  - Comprehensive documentation structure:
    - Getting started guide
    - Architecture documentation (overview, domain, application, interface adapters, infrastructure)
    - User guide (searching, downloading, preferences)
    - Development guides (setup, testing, contributing)
  - GitHub Actions workflow for automatic documentation deployment to GitHub Pages
  - `nodo-docs` console script for local documentation server
  - Shell script (`scripts/docs.sh`) for convenience
- User preferences use cases with inner Input/Output classes
  - `GetUserPreferences` - Retrieve current user preferences
  - `UpdateUserPreferences` - Update preferences (returns only changed fields)
  - `AddFavoritePath` - Add favorite download location (returns path and added flag)
  - `RemoveFavoritePath` - Remove favorite location (returns path and removed flag)
  - `AddFavoriteAggregator` - Add favorite aggregator (returns name and added flag)
  - `RemoveFavoriteAggregator` - Remove favorite aggregator (returns name and removed flag)
- Test suite for all user preferences use cases with 100% coverage
- Download management use cases
  - `ListDownloads` - List all downloads with filtering and sorting
  - `AddDownload` - Add and start a new download
  - `SearchTorrents` - Search torrents across multiple aggregators with deduplication
  - `GetDownloadStatus` - Get current status and progress of a download with real-time updates
- Application layer interfaces
  - `IAggregatorServiceRegistry` - Interface for accessing aggregator services by name
- Domain entity hashability
  - `TorrentSearchResult` now implements `__hash__` and `__eq__` based on magnet link
  - Enables set-based deduplication at the domain level
- Domain value objects
  - `TimeDuration` - Time duration value object with human-readable formatting
    - Validates non-negative and reasonable maximum values
    - Formats durations from seconds to days with proper pluralization
    - Supports comparison operations and hashing
- Domain entities
  - `DownloadStatus` - Status information entity for downloads from torrent client
    - Contains real-time progress, download/upload rates, ETA, and completion state
    - Moved from application layer to domain layer for better Clean Architecture compliance
- Test suite for download management use cases with 100% coverage

### Changed

- Documentation updated to accurately reflect current project state
  - Fixed project name references (`torrent-cli` → `nodo`)
  - Updated Python version requirement (3.11+ → 3.13+)
  - Corrected entity attributes (`id` → `id_`, `DownloadState` enum values)
  - Updated use case naming (`InputData`/`OutputData` → `Input`/`Output`)
  - Added missing `TimeDuration` value object documentation
  - Clarified `FilePath` is `pathlib.Path` (not separate value object)
  - Fixed exception names (`DomainException` → `DomainError`)
  - Updated interface method signatures to match actual implementations
  - Marked interface adapters and infrastructure layers as "to be implemented"
  - Updated use case count (10 implemented, 4 planned)
  - Added `IAggregatorServiceRegistry` interface documentation
- MkDocs navigation updated to include all documentation files
  - Added missing architecture documentation (layers, project structure, use cases, dependency injection)
  - Added missing development documentation (code quality, tech stack)
  - Added quick reference guide
  - Reorganized navigation structure for better discoverability
- CLAUDE.md updated with accurate project status and file paths
- `SearchTorrents` use case now accepts `IAggregatorServiceRegistry` interface instead of dict
  - Improves Clean Architecture compliance by depending on abstractions
- `SearchTorrents` validation: empty `aggregator_names` list now raises `ValidationError`
  - Only `None` triggers preference-based or all-available aggregator selection
- Deduplication in `SearchTorrents` now uses set-based approach instead of manual function
  - Leverages hashable `TorrentSearchResult` entity for efficient deduplication
- All test Mock objects now use `spec` parameter for type safety
  - Ensures only methods defined on interfaces can be called
  - Prevents typos and accidental method calls
  - Improves IDE autocomplete and type checking
- `GetDownloadStatus` now uses dictionary mapper for status determination
  - Replaces if/elif/else chain with cleaner, more extensible approach
- `GetDownloadStatus` formatting methods now validate input data
  - `_format_speed` and `_format_eta` return `None` for unreadable/invalid data
  - Allows use case to continue execution gracefully when data is unavailable
- `GetDownloadStatus._format_eta` now uses `TimeDuration` value object
  - Encapsulates time duration logic in domain layer
  - Simplifies formatting code and improves reusability
- `TorrentStatus` moved from application layer to domain layer as `DownloadStatus` entity
  - `TorrentStatus` dataclass moved from `application/interfaces/torrent_client.py` to `domain/entities/download_status.py`
  - Represents real-time status information from torrent client (progress, rates, ETA)
  - Improves Clean Architecture compliance by placing domain concepts in domain layer
- `DownloadStatus` enum renamed to `DownloadState` (value object)
  - Avoids naming conflict with new `DownloadStatus` entity
  - Represents download state (DOWNLOADING, COMPLETED, FAILED, PAUSED)
  - All references updated throughout codebase, tests, and documentation

### Removed

- `UserPreferencesDTO` - Replaced by use case-specific inner Output classes
- `user_preferences_mapper.py` - No longer needed with inner Output classes
- `SearchTorrents._deduplicate_results()` method - Replaced with set-based deduplication
- `TorrentStatus` from application layer - Moved to domain layer as `DownloadStatus` entity
- `DownloadStatus` enum (value object) - Renamed to `DownloadState` to avoid naming conflict


## [0.2.0] - 2025-12-08

### Added

- Domain layer exceptions
  - `DomainError` - Base exception for all domain errors
  - `ValidationError` - Input validation failures
  - `DownloadNotFoundError` - Download lookup failures
  - `DuplicateDownloadError` - Duplicate magnet link
  - `InvalidStateTransitionError` - Invalid status changes
  - `TorrentClientError` - Torrent client failures
  - `AggregatorError` - Aggregator search failures
  - `AggregatorTimeoutError` - Aggregator timeout
  - `FileSystemError` - File system operation failures

- Domain layer value objects
  - `MagnetLink` - Magnet URI with validation and info hash extraction
  - `FileSize` - File size with human-readable formatting and parsing
  - `AggregatorSource` - Torrent source/indexer name with canonical formatting
  - `DownloadStatus` - Enum (DOWNLOADING, COMPLETED, FAILED, PAUSED)

- Domain layer entities
  - `TorrentSearchResult` - Ephemeral search result entity
  - `Download` - Core persisted entity for tracking downloads
  - `UserPreferences` - Singleton preferences entity with modification tracking

- Project documentation
  - `PLAN.md` - Implementation plan with phases and progress tracking
  - `CLAUDE.md` - Updated with pytest style guidelines and layer clarifications

- Test suite for domain layer
  - Tests for all value objects (MagnetLink, FileSize, AggregatorSource, DownloadStatus)
  - Tests for all entities (TorrentSearchResult, Download, UserPreferences)
