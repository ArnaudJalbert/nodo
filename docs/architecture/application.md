# Application Layer

The Application layer contains application-specific business rules and use cases. It defines the interfaces that external services must implement, but does not implement them itself.

## Principles

- ✅ **Depends only on Domain layer** - No knowledge of external frameworks
- ✅ **Defines interfaces, not implementations** - Uses ABCs (Abstract Base Classes)
- ✅ **Use cases orchestrate domain entities** - Application logic coordinates domain objects
- ✅ **DTOs for cross-layer communication** - Data transfer objects for boundaries

## Components

### Interfaces (ABCs)

Interfaces define contracts that external services must implement. They are abstract base classes (ABCs) that specify method signatures without implementations.

#### IDownloadRepository

Interface for download persistence operations.

**Methods:**
- `save(download: Download) -> None` - Save or update a download
- `find_by_id(id_: UUID) -> Download | None` - Find by UUID
- `find_by_magnet_link(magnet_link: MagnetLink) -> Download | None` - Find by magnet link
- `find_all(status: DownloadStatus | None) -> list[Download]` - Find all, optionally filtered
- `delete(id_: UUID) -> bool` - Delete a download
- `exists_by_magnet_link(magnet_link: MagnetLink) -> bool` - Check existence

**Location**: `src/nodo/application/interfaces/download_repository.py`

#### IUserPreferencesRepository

Interface for user preferences persistence.

**Methods:**
- `get() -> UserPreferences` - Get preferences (creates defaults if none exist)
- `save(preferences: UserPreferences) -> None` - Save preferences

**Location**: `src/nodo/application/interfaces/user_preferences_repository.py`

#### IAggregatorService

Interface for torrent aggregator search operations.

**Properties:**
- `source: AggregatorSource` - The aggregator source this service represents

**Methods:**
- `search(query: str, max_results: int = 10) -> list[TorrentSearchResult]` - Search for torrents

**Raises:**
- `AggregatorError` - If the search fails
- `AggregatorTimeoutError` - If the search times out

**Location**: `src/nodo/application/interfaces/aggregator_service.py`

#### ITorrentClient

Interface for torrent client operations (e.g., qBittorrent).

**Methods:**
- `add_torrent(magnet_link: MagnetLink, download_path: str) -> str` - Add and start download
- `get_status(torrent_hash: str) -> TorrentStatus | None` - Get current status
- `pause(torrent_hash: str) -> bool` - Pause a torrent
- `resume(torrent_hash: str) -> bool` - Resume a paused torrent
- `remove(torrent_hash: str, delete_files: bool = False) -> bool` - Remove a torrent

**Raises:**
- `TorrentClientError` - If operations fail

**Location**: `src/nodo/application/interfaces/torrent_client.py`

### Data Transfer Objects (DTOs)

DTOs are simple data structures used to transfer data across layer boundaries. They contain no business logic.

#### DownloadDTO

Data transfer object for Download entities.

**Location**: `src/nodo/application/dtos/download_dto.py`

#### TorrentSearchResultDTO

Data transfer object for TorrentSearchResult entities.

**Location**: `src/nodo/application/dtos/torrent_search_result_dto.py`

#### UserPreferencesDTO

Data transfer object for UserPreferences entities.

**Location**: `src/nodo/application/dtos/user_preferences_dto.py`

### Use Cases (To Be Implemented)

Use cases orchestrate the flow of data and coordinate domain entities to achieve application goals.

#### User Preferences Use Cases

- `GetUserPreferences` - Load user preferences
- `UpdateUserPreferences` - Update user settings
- `AddFavoritePath` - Add favorite download location
- `RemoveFavoritePath` - Remove favorite location
- `AddFavoriteAggregator` - Add favorite source
- `RemoveFavoriteAggregator` - Remove favorite source

#### Download Management Use Cases

- `SearchTorrents` - Search across aggregators
- `AddDownload` - Add and start download
- `ListDownloads` - List downloads with filtering
- `GetDownloadStatus` - Get status and progress
- `RemoveDownload` - Remove download
- `PauseDownload` - Pause active download
- `ResumeDownload` - Resume paused download
- `RefreshDownloads` - Sync with torrent client

## Dependency Injection

Use cases receive their dependencies (repositories, services) through constructor injection. This allows:

- Easy testing with mocks
- Flexible implementation swapping
- Clear dependency declaration

## Example Use Case Structure

```python
class AddDownload:
    """Use case for adding a new download."""
    
    def __init__(
        self,
        download_repo: IDownloadRepository,
        torrent_client: ITorrentClient,
        preferences_repo: IUserPreferencesRepository
    ):
        self._download_repo = download_repo
        self._torrent_client = torrent_client
        self._preferences_repo = preferences_repo
    
    def execute(self, magnet_link: MagnetLink, title: str) -> DownloadDTO:
        # 1. Check for duplicates
        if self._download_repo.exists_by_magnet_link(magnet_link):
            raise DuplicateDownloadError(...)
        
        # 2. Get user preferences
        preferences = self._preferences_repo.get()
        
        # 3. Add to torrent client
        torrent_hash = self._torrent_client.add_torrent(
            magnet_link,
            str(preferences.download_path)
        )
        
        # 4. Create domain entity
        download = Download(
            magnet_link=magnet_link,
            title=title,
            file_path=preferences.download_path,
            source=...,
            size=...,
            status=DownloadStatus.DOWNLOADING
        )
        
        # 5. Persist
        self._download_repo.save(download)
        
        # 6. Return DTO
        return DownloadDTO.from_entity(download)
```

## Benefits

1. **Testability**: Use cases can be tested with mock implementations
2. **Flexibility**: Easy to swap implementations (e.g., SQLite → PostgreSQL)
3. **Clarity**: Clear separation between business logic and infrastructure
4. **Independence**: Application logic doesn't depend on external frameworks

## Next Steps

- [Interface Adapters](interface-adapters.md) - See how interfaces are implemented
- [Infrastructure](infrastructure.md) - See how use cases are wired together

