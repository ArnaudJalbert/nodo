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
- `save(download: Download) -> None` - Save or update a download (creates if new, updates if exists)
- `find_by_id(id_: UUID) -> Download | None` - Find by UUID
- `find_by_magnet_link(magnet_link: MagnetLink) -> Download | None` - Find by magnet link
- `find_all(status: DownloadStatus | None = None) -> list[Download]` - Find all, optionally filtered by status
- `delete(id_: UUID) -> bool` - Delete a download by UUID
- `exists_by_magnet_link(magnet_link: MagnetLink) -> bool` - Check if download exists by magnet link

**Location**: `src/nodo/application/interfaces/download_repository.py`

#### IUserPreferencesRepository

Interface for user preferences persistence.

**Methods:**
- `get() -> UserPreferences` - Get preferences (auto-creates defaults if none exist)
- `save(preferences: UserPreferences) -> None` - Save preferences

**Location**: `src/nodo/application/interfaces/user_preferences_repository.py`

#### IAggregatorService

Interface for torrent aggregator search operations.

**Properties:**
- `source: AggregatorSource` - The aggregator source this service represents (read-only property)

**Methods:**
- `search(query: str, max_results: int = 10) -> list[TorrentSearchResult]` - Search for torrents

**Raises:**
- `AggregatorError` - If the search fails
- `AggregatorTimeoutError` - If the search times out

**Location**: `src/nodo/application/interfaces/aggregator_service.py`

#### IAggregatorServiceRegistry

Interface for accessing aggregator services by name.

**Methods:**
- `get_service(aggregator_name: str) -> IAggregatorService | None` - Get service by name
- `get_all_names() -> list[str]` - Get all available aggregator names

**Location**: `src/nodo/application/interfaces/aggregator_service_registry.py`

#### ITorrentClient

Interface for torrent client operations (e.g., qBittorrent).

**Methods:**
- `add_torrent(magnet_link: MagnetLink, download_path: str) -> str` - Add and start download, returns torrent hash
- `get_status(torrent_hash: str) -> DownloadStatus | None` - Get current status
- `pause(torrent_hash: str) -> bool` - Pause a torrent
- `resume(torrent_hash: str) -> bool` - Resume a paused torrent
- `remove(torrent_hash: str, delete_files: bool = False) -> bool` - Remove a torrent

**Note:** `DownloadStatus` is a domain entity (not a DTO) located in `src/nodo/domain/entities/download_status.py`. It contains real-time status information from the torrent client.

**Raises:**
- `TorrentClientError` - If operations fail

**Location**: `src/nodo/application/interfaces/torrent_client.py`

### Data Transfer Objects (DTOs)

DTOs are simple data structures used to transfer data across layer boundaries. They contain no business logic.

#### DownloadDTO

Data transfer object for Download entities.

**Attributes:**
- `id_: str` - UUID as string
- `magnet_link: str` - Magnet link URI
- `title: str` - Download title
- `file_path: str` - File path as string
- `source: str` - Aggregator source as string
- `status: str` - Status name (e.g., "DOWNLOADING")
- `date_added: datetime` - When added
- `date_completed: datetime | None` - When completed
- `size: str` - Human-readable size string

**Location**: `src/nodo/application/dtos/download_dto.py`

#### TorrentSearchResultDTO

Data transfer object for TorrentSearchResult entities.

**Attributes:**
- `magnet_link: str` - Magnet link URI
- `title: str` - Torrent title
- `size: str` - Human-readable size string
- `seeders: int` - Number of seeders
- `leechers: int` - Number of leechers
- `source: str` - Aggregator source as string
- `date_found: datetime` - When found

**Location**: `src/nodo/application/dtos/torrent_search_result_dto.py`

**Note:** UserPreferences use cases return their output directly as dataclasses, not as a separate DTO.

### Use Cases

Use cases orchestrate the flow of data and coordinate domain entities to achieve application goals.

#### Implemented Use Cases ✅

**Download Management:**
- `SearchTorrents` - Search across aggregators
- `AddDownload` - Add and start download
- `ListDownloads` - List downloads with filtering and sorting
- `GetDownloadStatus` - Get status and progress
- `RemoveDownload` - Remove download with optional file deletion
- `PauseDownload` - Pause an active download
- `ResumeDownload` - Resume a paused download
- `RefreshDownloads` - Sync download statuses with torrent client

**Preferences Management:**
- `GetUserPreferences` - Load user preferences
- `UpdateUserPreferences` - Update user settings
- `AddFavoritePath` - Add favorite download location
- `RemoveFavoritePath` - Remove favorite location
- `AddFavoriteAggregator` - Add favorite source
- `RemoveFavoriteAggregator` - Remove favorite source

#### To Be Implemented ⏳

- None - All planned use cases are now implemented

**Location**: `src/nodo/application/use_cases/`

## Dependency Injection

Use cases receive their dependencies (repositories, services) through constructor injection. This allows:

- Easy testing with mocks
- Flexible implementation swapping
- Clear dependency declaration

## Example Use Case Structure

```python
class AddDownload:
    """Use case for adding a new download."""
    
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
    
    def __init__(
        self,
        download_repository: IDownloadRepository,
        torrent_client: ITorrentClient,
    ):
        self._download_repository = download_repository
        self._torrent_client = torrent_client
    
    def execute(self, input_data: Input) -> Output:
        # 1. Create value objects
        magnet_link = MagnetLink.from_string(input_data.magnet_link)
        aggregator_source = AggregatorSource.from_string(input_data.source)
        file_size = FileSize.from_string(input_data.size)
        file_path = Path(input_data.file_path)
        
        # 2. Check for duplicates
        if self._download_repository.exists_by_magnet_link(magnet_link):
            raise DuplicateDownloadError(...)
        
        # 3. Create domain entity
        download = Download(
            magnet_link=magnet_link,
            title=input_data.title.strip(),
            file_path=file_path,
            source=aggregator_source,
            size=file_size,
            # status defaults to DOWNLOADING
        )
        
        # 4. Persist
        self._download_repository.save(download)
        
        # 5. Start in torrent client
        self._torrent_client.add_torrent(magnet_link, str(file_path.parent))
        
        # 6. Convert to DTO and return
        return Output(download=AddDownload._to_dto(download))
```

## Benefits

1. **Testability**: Use cases can be tested with mock implementations
2. **Flexibility**: Easy to swap implementations (e.g., SQLite → PostgreSQL)
3. **Clarity**: Clear separation between business logic and infrastructure
4. **Independence**: Application logic doesn't depend on external frameworks

## Next Steps

- [Interface Adapters](interface-adapters.md) - See how interfaces are implemented
- [Infrastructure](infrastructure.md) - See how use cases are wired together

