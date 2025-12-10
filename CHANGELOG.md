# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] 2025-12-08

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
- Test suite for download management use cases with 100% coverage

### Changed

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

### Removed

- `UserPreferencesDTO` - Replaced by use case-specific inner Output classes
- `user_preferences_mapper.py` - No longer needed with inner Output classes
- `SearchTorrents._deduplicate_results()` method - Replaced with set-based deduplication


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
