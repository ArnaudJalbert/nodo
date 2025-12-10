# Domain Model

## Entities

### Download (Core Entity)

Represents a torrent that has been downloaded or is currently downloading.

**Attributes:**
- `id_`: UUID - Primary key (auto-generated)
- `magnet_link`: MagnetLink - Torrent identifier
- `title`: str - Download name
- `file_path`: Path - Local storage location (pathlib.Path)
- `source`: AggregatorSource - Origin aggregator
- `status`: DownloadState - Current state (default: DOWNLOADING)
- `date_added`: datetime - When initiated (auto-generated)
- `date_completed`: datetime | None - When finished
- `size`: FileSize - Total size

**DownloadState Enum (Value Object):**
- `DOWNLOADING` - In progress (auto-generated value)
- `COMPLETED` - Finished (auto-generated value)
- `FAILED` - Error occurred (auto-generated value)
- `PAUSED` - Temporarily stopped (auto-generated value)

**Note:** Uses `enum.auto()` for values, accessed via `.name` property.

---

### TorrentSearchResult (Ephemeral)

Represents search results from aggregators. Not persisted.

**Attributes:**
- `magnet_link`: MagnetLink - Unique identifier
- `title`: str - Torrent name
- `size`: FileSize - File size
- `seeders`: int - Number of seeders
- `leechers`: int - Number of leechers
- `source`: AggregatorSource - Which aggregator
- `date_found`: datetime - When retrieved

**Usage:** Exists in memory during search, converted to Download when selected.

---

### DownloadStatus (Entity)

Status information for a download from the torrent client.

**Attributes:**
- `progress`: float - Download progress as percentage (0.0 to 100.0)
- `download_rate`: int - Current download speed in bytes per second
- `upload_rate`: int - Current upload speed in bytes per second
- `eta_seconds`: int | None - Estimated time remaining in seconds, None if unknown
- `is_complete`: bool - Whether the download is complete
- `is_paused`: bool - Whether the download is paused

**Usage:** Returned by torrent client interface to provide real-time status information.

---

### UserPreferences (Singleton)

Stores user configuration. Only one instance exists.

**Attributes:**
- `id_`: UUID - Always `00000000-0000-0000-0000-000000000001` (well-known, `USER_PREFERENCES_ID`)
- `default_download_path`: Path - Default save location (pathlib.Path)
- `favorite_paths`: list[Path] - Quick-select locations
- `favorite_aggregators`: list[AggregatorSource] - Preferred sources
- `max_concurrent_downloads`: int - Simultaneous downloads (1-10, default: 3)
- `auto_start_downloads`: bool - Auto-start on add (default: True)
- `date_created`: datetime - Initial creation (auto-generated)
- `date_modified`: datetime - Last update (auto-updated by decorator)

**Business Rules:**
- Singleton pattern (only one instance)
- `default_download_path` must always be valid
- `max_concurrent_downloads` between 1 and 10
- Empty `favorite_aggregators` means use all available
- All modifications update `date_modified`

**Domain Methods:**
```python
def add_favorite_path(self, path: Path) -> bool  # Returns True if added
def remove_favorite_path(self, path: Path) -> bool  # Returns True if removed
def add_favorite_aggregator(self, source: AggregatorSource) -> bool  # Returns True if added
def remove_favorite_aggregator(self, source: AggregatorSource) -> bool  # Returns True if removed
def update_default_path(self, path: Path) -> None
def update_max_concurrent_downloads(self, max_count: int) -> None
def update_auto_start(self, enabled: bool) -> None

@classmethod
def create_default(cls) -> "UserPreferences"
```

**Note:** Methods that modify state use the `@updates_modified_date` decorator to automatically update `date_modified`.

---

## Value Objects

### MagnetLink

Immutable magnet URI for BitTorrent.

**Validation:**
- Must start with `magnet:?`
- Must contain `xt=urn:btih:` (info hash)
- Info hash: 40 chars (SHA-1) or 64 chars (SHA-256)

**Methods:**
```python
@classmethod
def from_string(uri: str) -> MagnetLink
def get_info_hash() -> str
def __str__() -> str
def __eq__(other) -> bool  # Compare by info hash
```

---

### FileSize

Immutable file size with human-readable formatting.

**Storage:** Bytes (canonical)

**Units:** B, KB, MB, GB, TB (1024-based)

**Methods:**
```python
@classmethod
def from_bytes(size: int) -> FileSize
@classmethod
def from_string(size: str) -> FileSize  # Parse "1.5 GB"
def to_human_readable() -> str
def __str__() -> str
def __eq__(other) -> bool
def __lt__(other) -> bool
```

---

### FilePath

The domain uses `pathlib.Path` directly (not a separate value object).

**Why pathlib.Path:**
- Built-in validation
- Cross-platform
- Rich API
- Standard library (no external dependencies)

**Usage in Domain:**
- `Download.file_path: Path`
- `UserPreferences.default_download_path: Path`
- `UserPreferences.favorite_paths: list[Path]`

**Common Operations:**
```python
path.exists() -> bool
path.is_file() -> bool
path.is_dir() -> bool
path.parent -> Path
path.name -> str
path.resolve() -> Path
```

---

### AggregatorSource

Immutable source aggregator identifier.

**Attributes:**
- `name`: str - Canonical aggregator name

**Validation:**
- Non-empty
- From known list
- Case-insensitive but stored canonically

**Supported Aggregators:**
- `1337x`
- `ThePirateBay`
- `RARBG`
- `Nyaa`
- `TorrentGalaxy`
- `LimeTorrents`

**Methods:**
```python
@classmethod
def from_string(name: str) -> AggregatorSource
def __str__() -> str
def __eq__(other) -> bool  # Case-insensitive
```

---

### DownloadState

Immutable enumeration representing the current state of a download.

**Values:**
- `DOWNLOADING` - Download is in progress
- `COMPLETED` - Download finished successfully
- `FAILED` - Download failed
- `PAUSED` - Download is paused

**Usage:**
```python
from nodo.domain.value_objects import DownloadState

download.status = DownloadState.COMPLETED
if download.status == DownloadState.DOWNLOADING:
    # ...
```

**Note:** Uses `enum.auto()` for values, accessed via `.name` property.

---

### TimeDuration

Immutable time duration with human-readable formatting.

**Storage:** Seconds (canonical)

**Methods:**
```python
@classmethod
def from_seconds(seconds: int | None) -> TimeDuration | None
def to_human_readable() -> str
def __str__() -> str
def __eq__(other) -> bool
def __lt__(other) -> bool
```

**Example:**
```python
duration = TimeDuration.from_seconds(3661)
print(duration)  # "1 hour 1 minute 1 second"
```

---

## Domain Exceptions

All exceptions inherit from `DomainError`:

```python
class DomainError(Exception):
    """Base exception for all domain errors"""

class ValidationError(DomainError):
    """Invalid input"""

class DownloadNotFoundError(DomainError):
    """Download doesn't exist"""

class DuplicateDownloadError(DomainError):
    """Download already exists"""

class InvalidStateTransitionError(DomainError):
    """Invalid status change"""

class TorrentClientError(DomainError):
    """Torrent client operation failed"""

class AggregatorError(DomainError):
    """Aggregator search failed"""

class AggregatorTimeoutError(AggregatorError):
    """Aggregator search timeout"""

class FileSystemError(DomainError):
    """File system operation failed"""
```

**Location:** `src/nodo/domain/exceptions/`

---

## Entity Relationships

```
TorrentSearchResult (ephemeral)
    ↓ user selects
Download (persisted)
    ↓ references
UserPreferences (singleton)
```

**Key Points:**
- TorrentSearchResult → Download when user adds
- Download stores download-specific settings
- UserPreferences stores global settings
- No Download → TorrentSearchResult reverse relationship

---

## Design Principles

1. **Separation of Concerns** - Each entity has one clear purpose
2. **Immutability** - Value objects cannot change after creation
3. **Validation** - Enforced at creation time
4. **Domain Logic** - Business rules live in entities
5. **No Infrastructure** - Domain layer has no external dependencies

---

## DTO Pattern

DTOs transfer data between layers. Always defined as frozen dataclasses.

**Standard DTO Structure:**
```python
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True, slots=True)
class DownloadDTO:
    """Shared DTO for Download entity"""
    id: str  # UUID as string
    magnet_link: str
    title: str
    file_path: str
    source: str
    status: str
    date_added: datetime
    date_completed: datetime | None
    size: str
```

**DTO Organization:**
- **Shared DTOs** - `src/nodo/application/dtos/` (separate files: `download_dto.py`, `torrent_search_result_dto.py`)
- **Use Case DTOs** - Inner classes named `Input` and `Output`

**Example Use Case DTO:**
```python
class AddDownload:
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        magnet_link: str
        title: str
        source: str
        size: str
        file_path: str
    
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        download: DownloadDTO
```

**Benefits:**
- Encapsulation - DTOs tightly coupled to use case
- Discoverability - Easy to find
- Namespacing - No conflicts
- Immutability - `frozen=True`
- Type safety - `kw_only=True`
- Memory efficient - `slots=True`
