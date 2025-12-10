# Use Cases

## Summary

**10 use cases** currently implemented, organized into two categories:

**Download Management (4):**
1. SearchTorrents ✅
2. AddDownload ✅
3. ListDownloads ✅
4. GetDownloadStatus ✅

**Preferences Management (6):**
5. GetUserPreferences ✅
6. UpdateUserPreferences ✅
7. AddFavoritePath ✅
8. RemoveFavoritePath ✅
9. AddFavoriteAggregator ✅
10. RemoveFavoriteAggregator ✅

**To Be Implemented:**
- RemoveDownload
- PauseDownload
- ResumeDownload
- RefreshDownloads

---

## Use Case Template

Each use case follows this structure:

```python
class UseCase:
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        # Input fields
        pass
    
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        # Output fields
        pass
    
    def __init__(self, dependencies: Interface):
        # Inject dependencies via interfaces (ABC)
        pass
    
    def execute(self, input_data: Input) -> Output:
        # Business logic
        pass
```

---

## Download Management

### 1. SearchTorrents

**Purpose:** Search for torrents across aggregators

**Dependencies:**
- `IAggregatorServiceRegistry` - Registry for accessing aggregator services
- `IUserPreferencesRepository` - For getting favorite aggregators

**Input:**
- `query: str` - Search query string
- `aggregator_names: list[str] | None` - Optional list of aggregator names
- `max_results: int` - Maximum results per aggregator (default: 10)

**Output:**
- `results: tuple[TorrentSearchResultDTO, ...]` - Search results
- `failed_searches: tuple[FailedSearch, ...]` - Failed aggregator searches

**Flow:**
1. Validate query (raise `ValidationError` if empty)
2. Validate `max_results >= 1`
3. Determine aggregators:
   - Use `input.aggregator_names` if provided
   - Else load `preferences.favorite_aggregators`
   - If empty, use all available from registry
4. Validate aggregator names if provided
5. Search each aggregator (catch `AggregatorError` and `AggregatorTimeoutError`)
6. Deduplicate by magnet link (using set)
7. Sort by seeders (descending)
8. Return results and failed searches

**Exceptions:**
- `ValidationError` - Empty query, invalid max_results, or invalid aggregator names
- `AggregatorError` - All aggregators failed or no aggregators available

---

### 2. AddDownload

**Purpose:** Add and start a torrent download

**Dependencies:**
- `IDownloadRepository` - For persistence
- `ITorrentClient` - For starting download

**Input:**
- `magnet_link: str` - The magnet link URI
- `title: str` - Name of the downloaded content
- `source: str` - Which aggregator it was downloaded from
- `size: str` - Human-readable size string (e.g., "1.5 GB")
- `file_path: str` - The file path where download will be stored

**Output:**
- `download: DownloadDTO` - The created download

**Flow:**
1. Create value objects (`MagnetLink`, `AggregatorSource`, `FileSize`, `Path`)
2. Validate title (not empty)
3. Check for duplicates (`repository.exists_by_magnet_link`)
4. Create `Download` entity (status=DOWNLOADING by default)
5. Save to repository
6. Start in torrent client (using parent directory of file_path)
7. Convert to DTO and return

**Exceptions:**
- `ValidationError` - Invalid magnet/size/source or empty title
- `DuplicateDownloadError` - Already exists
- `TorrentClientError` - Failed to start in client

---

### 3. ListDownloads

**Purpose:** Retrieve all downloads with optional filtering

**Dependencies:**
- `IDownloadRepository` - For querying downloads

**Input:**
- `status: str | None` - Optional status filter

**Output:**
- `downloads: tuple[DownloadDTO, ...]` - List of downloads

**Flow:**
1. Convert status string to `DownloadState` enum if provided
2. Query `repository.find_all(status)`
3. Convert entities to DTOs
4. Return tuple of DTOs

**Exceptions:**
- `ValidationError` - Invalid status string

---

### 4. GetDownloadStatus

**Purpose:** Get current status and progress

**Dependencies:**
- `IDownloadRepository` - For retrieving download
- `ITorrentClient` - For getting current status

**Input:**
- `download_id: str` - UUID of the download

**Output:**
- `download: DownloadDTO` - Download with current status
- `status: DownloadStatus | None` - Current torrent client status (if available)

**Flow:**
1. Validate and convert UUID string
2. Retrieve download from repository
3. Query `torrent_client.get_status()` using magnet link hash
4. Return DTO and status

**Exceptions:**
- `ValidationError` - Invalid UUID string
- `DownloadNotFoundError` - Download not found
- `TorrentClientError` - Client query failed

---

### 5. RemoveDownload

**Status:** ⏳ To be implemented

**Purpose:** Remove download from tracking, optionally delete files

**Dependencies:**
- `IDownloadRepository`
- `ITorrentClient`

**Planned Flow:**
1. Validate UUID
2. Retrieve download
3. Remove from torrent client
4. Delete files if `delete_files=True`
5. Delete from repository
6. Return success

**Exceptions:**
- `ValidationError` - Invalid UUID
- `DownloadNotFoundError` - Download not found
- `FileSystemError` - File deletion failed
- `TorrentClientError` - Client removal failed

---

### 6. PauseDownload

**Status:** ⏳ To be implemented

**Purpose:** Pause an active download

**Dependencies:**
- `IDownloadRepository`
- `ITorrentClient`

**Planned Flow:**
1. Validate UUID
2. Retrieve download
3. Verify status is DOWNLOADING
4. Pause in torrent client
5. Update entity status to PAUSED
6. Save entity
7. Return DTO

**Exceptions:**
- `ValidationError` - Invalid UUID
- `DownloadNotFoundError` - Download not found
- `InvalidStateTransitionError` - Cannot pause from current status
- `TorrentClientError` - Pause failed

---

### 7. ResumeDownload

**Status:** ⏳ To be implemented

**Purpose:** Resume a paused download

**Dependencies:**
- `IDownloadRepository`
- `ITorrentClient`

**Planned Flow:**
1. Validate UUID
2. Retrieve download
3. Verify status is PAUSED
4. Resume in torrent client
5. Update entity status to DOWNLOADING
6. Save entity
7. Return DTO

**Exceptions:**
- `ValidationError` - Invalid UUID
- `DownloadNotFoundError` - Download not found
- `InvalidStateTransitionError` - Cannot resume from current status
- `TorrentClientError` - Resume failed

---

### 8. RefreshDownloads

**Status:** ⏳ To be implemented

**Purpose:** Sync download statuses with torrent client (can be scheduled)

**Dependencies:**
- `IDownloadRepository`
- `ITorrentClient`

**Planned Flow:**
1. Get all active downloads (DOWNLOADING, PAUSED)
2. For each download:
   - Query `torrent_client.get_status()`
   - Compare with entity status
   - Update if different (set COMPLETED if progress=100%)
   - Save updated entity
   - Record errors but continue
3. Return counts and errors

**Exceptions:**
- Generally catches errors rather than raising
- Only raises on critical repository failures

**Note:** Scheduling/timing handled by external layer.

---

## Preferences Management

### 9. GetUserPreferences

**Purpose:** Load user preferences (typically at startup)

**Dependencies:**
- `IUserPreferencesRepository` - For retrieving preferences

**Input:**
- (No input required)

**Output:**
- `preferences: UserPreferencesDTO` - User preferences

**Flow:**
1. Call `repository.get()` (auto-creates if missing)
2. Convert entity to DTO
3. Return DTO

**Exceptions:**
- Rarely raises (repository handles creation)

---

### 10. UpdateUserPreferences

**Purpose:** Update one or more preference settings

**Dependencies:**
- `IUserPreferencesRepository` - For loading and saving preferences

**Input:**
- `default_download_path: str | None` - New default path
- `max_concurrent_downloads: int | None` - New max concurrent downloads
- `auto_start_downloads: bool | None` - New auto-start setting

**Output:**
- `preferences: UserPreferencesDTO` - Updated preferences

**Flow:**
1. Load existing preferences
2. For each non-None input field:
   - Validate value
   - Call entity update method
3. Save updated entity
4. Return DTO

**Exceptions:**
- `ValidationError` - Invalid path or max_concurrent_downloads (not 1-10)
- `FileSystemError` - Invalid default_download_path

**Note:** Only updates provided fields (partial updates).

---

### 11. AddFavoritePath

**Purpose:** Add path to favorites

**Dependencies:**
- `IUserPreferencesRepository` - For loading and saving preferences

**Input:**
- `path: str` - Path to add to favorites

**Output:**
- `preferences: UserPreferencesDTO` - Updated preferences
- `was_added: bool` - Whether the path was actually added

**Flow:**
1. Validate and create Path
2. Load preferences
3. Call `preferences.add_favorite_path(path)` (returns bool)
4. Save entity
5. Return DTO with `was_added` flag

**Exceptions:**
- `ValidationError` - Invalid path
- `FileSystemError` - Path doesn't exist

**Note:** Idempotent - duplicates ignored (returns `was_added=False`).

---

### 12. RemoveFavoritePath

**Purpose:** Remove path from favorites

**Dependencies:**
- `IUserPreferencesRepository` - For loading and saving preferences

**Input:**
- `path: str` - Path to remove from favorites

**Output:**
- `preferences: UserPreferencesDTO` - Updated preferences
- `was_removed: bool` - Whether the path was actually removed

**Flow:**
1. Convert to Path
2. Load preferences
3. Call `preferences.remove_favorite_path(path)` (returns bool)
4. Save entity
5. Return DTO with `was_removed` flag

**Exceptions:**
- `ValidationError` - Invalid path

**Note:** Idempotent - removing non-existent path is not an error (returns `was_removed=False`).

---

### 13. AddFavoriteAggregator

**Purpose:** Add aggregator to favorites

**Dependencies:**
- `IUserPreferencesRepository` - For loading and saving preferences

**Input:**
- `aggregator_name: str` - Name of aggregator to add

**Output:**
- `preferences: UserPreferencesDTO` - Updated preferences
- `was_added: bool` - Whether the aggregator was actually added

**Flow:**
1. Validate and create AggregatorSource
2. Load preferences
3. Call `preferences.add_favorite_aggregator(source)` (returns bool)
4. Save entity
5. Return DTO with `was_added` flag

**Exceptions:**
- `ValidationError` - Unknown aggregator

**Note:** Idempotent - duplicates ignored (returns `was_added=False`).

---

### 14. RemoveFavoriteAggregator

**Purpose:** Remove aggregator from favorites

**Dependencies:**
- `IUserPreferencesRepository` - For loading and saving preferences

**Input:**
- `aggregator_name: str` - Name of aggregator to remove

**Output:**
- `preferences: UserPreferencesDTO` - Updated preferences
- `was_removed: bool` - Whether the aggregator was actually removed

**Flow:**
1. Convert to AggregatorSource
2. Load preferences
3. Call `preferences.remove_favorite_aggregator(source)` (returns bool)
4. Save entity
5. Return DTO with `was_removed` flag

**Exceptions:**
- `ValidationError` - Unknown aggregator

**Note:** Idempotent - removing non-existent aggregator is not an error (returns `was_removed=False`).

---

## Repository Interfaces

### IDownloadRepository

```python
def save(download: Download) -> None
def find_by_id(id_: UUID) -> Download | None
def find_by_magnet_link(magnet_link: MagnetLink) -> Download | None
def find_all(status: DownloadStatus | None = None) -> list[Download]
def delete(id_: UUID) -> bool
def exists_by_magnet_link(magnet_link: MagnetLink) -> bool
```

**Location:** `src/nodo/application/interfaces/download_repository.py`

### IUserPreferencesRepository

```python
def get() -> UserPreferences  # Auto-creates if missing
def save(preferences: UserPreferences) -> None
```

**Location:** `src/nodo/application/interfaces/user_preferences_repository.py`

---

## External Service Interfaces

### IAggregatorService

```python
@property
def source() -> AggregatorSource

def search(query: str, max_results: int = 10) -> list[TorrentSearchResult]
```

**Raises:**
- `AggregatorError` - If search fails
- `AggregatorTimeoutError` - If search times out

**Location:** `src/nodo/application/interfaces/aggregator_service.py`

### IAggregatorServiceRegistry

```python
def get_service(aggregator_name: str) -> IAggregatorService | None
def get_all_names() -> list[str]
```

**Location:** `src/nodo/application/interfaces/aggregator_service_registry.py`

### ITorrentClient

```python
def add_torrent(magnet_link: MagnetLink, download_path: str) -> str  # Returns torrent hash
def get_status(torrent_hash: str) -> DownloadStatus | None
def pause(torrent_hash: str) -> bool
def resume(torrent_hash: str) -> bool
def remove(torrent_hash: str, delete_files: bool = False) -> bool
```

**Note:** `DownloadStatus` is a domain entity (not a DTO) located in `src/nodo/domain/entities/download_status.py`. It contains real-time status information from the torrent client.

**Raises:**
- `TorrentClientError` - If operations fail

**Location:** `src/nodo/application/interfaces/torrent_client.py`

---

## Error Handling Guidelines

1. **Always raise exceptions** - Don't return error codes
2. **Be specific** - Use the most specific exception type
3. **Include context** - Pass helpful error messages
4. **Let it bubble** - Don't catch unless you can handle
5. **Document** - List possible exceptions in docstrings

**Example:**
```python
def execute(self, input_data: Input) -> Output:
    try:
        magnet = MagnetLink.from_string(input_data.magnet_link)
    except ValueError as e:
        raise ValidationError(f"Invalid magnet link: {e}")
    
    if self.repository.exists_by_magnet_link(magnet):
        raise DuplicateDownloadError(f"Download already exists: {magnet.info_hash}")
    
    # ... rest of use case
```

---

## Dependency Summary

| Use Case | Repositories | External Services |
|----------|-------------|-------------------|
| SearchTorrents | UserPreferences | Aggregator |
| AddDownload | Download, UserPreferences | TorrentClient |
| ListDownloads | Download | - |
| GetDownloadStatus | Download | TorrentClient |
| RemoveDownload | Download | TorrentClient, FileSystem |
| PauseDownload | Download | TorrentClient |
| ResumeDownload | Download | TorrentClient |
| RefreshDownloads | Download | TorrentClient |
| GetUserPreferences | UserPreferences | - |
| UpdateUserPreferences | UserPreferences | - |
| AddFavoritePath | UserPreferences | - |
| RemoveFavoritePath | UserPreferences | - |
| AddFavoriteAggregator | UserPreferences | - |
| RemoveFavoriteAggregator | UserPreferences | - |