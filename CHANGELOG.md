# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] 2025-12-08

### Added

- Application layer data transfer objects (DTOs)
  - `DownloadDTO` - Data transfer object for Download entity
  - `TorrentSearchResultDTO` - Data transfer object for TorrentSearchResult entity
  - `UserPreferencesDTO` - Data transfer object for UserPreferences entity
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
