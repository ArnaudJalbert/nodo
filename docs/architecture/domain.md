# Domain Layer

The Domain layer is the **innermost layer** of the Clean Architecture. It contains the core business logic and is completely independent of external frameworks, databases, and UI concerns.

## Principles

- ✅ **No external dependencies** - Only Python standard library
- ✅ **Pure business logic** - No I/O, no frameworks
- ✅ **Most stable layer** - Rarely changes when external systems change
- ✅ **Testable in isolation** - No mocks needed

## Components

### Entities

Entities are the core business objects that encapsulate enterprise-wide business rules.

#### Download

The main persisted entity representing a torrent download.

**Attributes:**
- `id_`: UUID - Unique identifier
- `magnet_link`: MagnetLink - The magnet link used to download
- `title`: str - Name of the downloaded content
- `file_path`: Path - Local file system path where content is saved
- `source`: AggregatorSource - Which aggregator it was downloaded from
- `status`: DownloadStatus - Current status (DOWNLOADING, COMPLETED, FAILED, PAUSED)
- `size`: FileSize - Total size of the download
- `date_added`: datetime - When the download was initiated
- `date_completed`: datetime | None - When the download finished

**Location**: `src/nodo/domain/entities/download.py`

#### TorrentSearchResult

An ephemeral entity representing a torrent found from an aggregator search. Not persisted to the database.

**Attributes:**
- `magnet_link`: MagnetLink - Unique identifier for the torrent
- `title`: str - Name/title of the torrent
- `size`: FileSize - File size of the torrent
- `seeders`: int - Number of seeders
- `leechers`: int - Number of leechers
- `source`: AggregatorSource - Which aggregator it came from
- `date_found`: datetime - When this result was retrieved

**Location**: `src/nodo/domain/entities/torrent_search_result.py`

#### UserPreferences

A singleton entity representing user configuration and preferences.

**Attributes:**
- `download_path`: Path - Default download path
- `max_concurrent_downloads`: int - Maximum concurrent downloads
- `auto_start_downloads`: bool - Whether to auto-start downloads
- `favorite_paths`: list[Path] - Favorite download locations
- `favorite_aggregators`: list[AggregatorSource] - Preferred aggregator sources

**Location**: `src/nodo/domain/entities/user_preferences.py`

### Value Objects

Value objects are immutable objects that represent domain concepts. They have no identity and are defined by their attributes.

#### MagnetLink

Represents a magnet URI with validation.

**Location**: `src/nodo/domain/value_objects/magnet_link.py`

**Features:**
- Validates magnet URI format
- Immutable

#### FileSize

Represents a file size with human-readable formatting.

**Location**: `src/nodo/domain/value_objects/file_size.py`

**Features:**
- Stores size in bytes
- Provides human-readable formatting (e.g., "1.5 GB")
- Immutable

#### DownloadStatus

Enumeration representing the current status of a download.

**Values:**
- `DOWNLOADING` - The download is currently in progress
- `COMPLETED` - The download has finished successfully
- `FAILED` - The download has failed
- `PAUSED` - The download has been paused by the user

**Location**: `src/nodo/domain/value_objects/download_status.py`

#### AggregatorSource

Represents a torrent source/indexer name.

**Location**: `src/nodo/domain/value_objects/aggregator_source.py`

**Features:**
- Validates source names
- Examples: "1337x", "ThePirateBay"

### Exceptions

Domain-specific exceptions that represent business rule violations.

#### Base Exception

- `DomainException` - Base exception for all domain exceptions

#### Validation Exceptions

- `ValidationError` - Input validation failures

#### Download Exceptions

- `DownloadNotFoundError` - Download lookup failures
- `DuplicateDownloadError` - Duplicate magnet link
- `InvalidStateTransitionError` - Invalid status changes

#### External Service Exceptions

- `TorrentClientError` - Torrent client failures
- `AggregatorError` - Aggregator search failures
- `AggregatorTimeoutError` - Aggregator timeout

#### System Exceptions

- `FileSystemError` - File system operation failures

**Location**: `src/nodo/domain/exceptions/`

## Design Patterns

### Dataclasses

Entities use Python dataclasses with:
- `slots=True` for memory efficiency
- `kw_only=True` for explicit keyword arguments
- `frozen=True` for value objects (immutability)

### Factory Methods

Entities may include factory methods for creating instances with sensible defaults.

## Testing

Domain layer code should have **100% test coverage**. Tests are located in `tests/nodo/domain/`.

Since the domain layer has no external dependencies, tests are straightforward and don't require mocks.

## Example Usage

```python
from nodo.domain.entities import Download
from nodo.domain.value_objects import MagnetLink, FileSize, AggregatorSource, DownloadStatus

# Create a download entity
magnet = MagnetLink("magnet:?xt=urn:btih:...")
size = FileSize(1_500_000_000)  # 1.5 GB
source = AggregatorSource("1337x")

download = Download(
    magnet_link=magnet,
    title="Ubuntu 24.04",
    file_path=Path("/downloads/ubuntu"),
    source=source,
    size=size,
    status=DownloadStatus.DOWNLOADING
)
```

## Next Steps

- [Application Layer](application.md) - See how the domain is used by the application layer
- [Interface Adapters](interface-adapters.md) - See how repositories persist domain entities

