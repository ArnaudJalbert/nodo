# Interface Adapters Layer

The Interface Adapters layer implements the interfaces defined in the Application layer. It adapts data between the application's use cases and external systems like databases, APIs, and file systems.

## Current Status

**⏳ To Be Implemented** - This layer is currently empty (only contains `__init__.py`).

The domain and application layers are complete, but the interface adapters that connect them to external systems are pending implementation.

## Principles

- ✅ **Implements Application interfaces** - Concrete implementations of ABCs
- ✅ **Depends on Application and Domain** - Uses interfaces and entities
- ✅ **Handles data transformation** - Converts between external formats and domain entities
- ✅ **Isolated from Infrastructure** - Doesn't know about CLI or DI container

## Components

### Repository Implementations

**Status:** ⏳ To be implemented

Repositories provide persistence for domain entities. They implement the repository interfaces defined in the Application layer.

#### SQLiteDownloadRepository

**Planned:** SQLAlchemy-based implementation of `IDownloadRepository` using SQLite.

**Responsibilities:**
- Map `Download` entities to database records
- Handle CRUD operations
- Convert between domain entities and database models

**Location**: `src/nodo/interface_adapters/repositories/` (to be implemented)

**Example Structure:**
```python
class SQLiteDownloadRepository(IDownloadRepository):
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, download: Download) -> None:
        # Convert entity to ORM model
        # Save to database
        pass
    
    def find_by_id(self, id_: UUID) -> Download | None:
        # Query database
        # Convert ORM model to entity
        pass
```

#### SQLiteUserPreferencesRepository

**Planned:** SQLAlchemy-based implementation of `IUserPreferencesRepository` using SQLite.

**Responsibilities:**
- Persist `UserPreferences` singleton
- Handle default preferences creation

**Location**: `src/nodo/interface_adapters/repositories/` (to be implemented)

### Service Adapters

**Status:** ⏳ To be implemented

Service adapters implement interfaces for external services.

#### QBittorrentAdapter

**Planned:** Adapter for qBittorrent Web API, implementing `ITorrentClient`.

**Responsibilities:**
- Communicate with qBittorrent via HTTP API
- Map qBittorrent responses to domain value objects
- Handle authentication and error cases

**Location**: `src/nodo/interface_adapters/services/` (to be implemented)

**Example Structure:**
```python
class QBittorrentAdapter(ITorrentClient):
    def __init__(self, base_url: str, username: str, password: str):
        self._client = QBittorrentClient(base_url, username, password)
    
    def add_torrent(self, magnet_link: MagnetLink, download_path: str) -> str:
        # Call qBittorrent API
        # Return torrent hash
        pass
    
    def get_status(self, torrent_hash: str) -> DownloadStatus | None:
        # Query qBittorrent API
        # Convert to DownloadStatus entity
        pass
```

#### Aggregator Adapters

**Planned:** Adapters for various torrent aggregator websites, implementing `IAggregatorService`.

**Base Adapter:**
- `AggregatorAdapter` - Base class with common functionality (to be implemented)

**Specific Implementations:**
- `The1337xAdapter` - 1337x aggregator (to be implemented)
- `ThePirateBayAdapter` - ThePirateBay aggregator (to be implemented)
- (More aggregators as needed)

**Responsibilities:**
- Scrape or use APIs from aggregator websites
- Parse HTML/JSON responses
- Convert to `TorrentSearchResult` entities
- Handle rate limiting and errors

**Location**: `src/nodo/interface_adapters/services/aggregators/` (to be implemented)

## Data Transformation

Interface adapters are responsible for converting between:

1. **Domain entities** ↔ **Database models** (repositories)
2. **Domain entities** ↔ **External API formats** (service adapters)
3. **Domain value objects** ↔ **External representations**

### Example: Entity to Database Model

```python
def _to_orm_model(self, download: Download) -> DownloadModel:
    return DownloadModel(
        id=str(download.id_),
        magnet_link=str(download.magnet_link),
        title=download.title,
        file_path=str(download.file_path),
        source=str(download.source),
        status=download.status.value,
        size_bytes=download.size.bytes,
        date_added=download.date_added,
        date_completed=download.date_completed
    )

def _to_entity(self, model: DownloadModel) -> Download:
    return Download(
        id_=UUID(model.id),
        magnet_link=MagnetLink(model.magnet_link),
        title=model.title,
        file_path=Path(model.file_path),
        source=AggregatorSource(model.source),
        status=DownloadState(model.status),
        size=FileSize(model.size_bytes),
        date_added=model.date_added,
        date_completed=model.date_completed
    )
```

## Error Handling

Interface adapters should:

- Catch external system errors
- Convert to domain exceptions when appropriate
- Handle network timeouts, connection errors, etc.
- Provide meaningful error messages

## Testing

Interface adapters can be tested with:

- **Integration tests** - Against real databases/APIs (in test environments)
- **Unit tests** - With mocked external dependencies
- **Contract tests** - Verify interface compliance

## Protocols

**Status:** ⏳ To be implemented

Protocols define structural typing for dependencies:

- `SQLAlchemySessionProtocol` - Database session protocol (to be implemented)
- `QBittorrentClientProtocol` - qBittorrent API protocol (to be implemented)

**Location**: `src/nodo/interface_adapters/protocols/` (to be implemented)

## Current Project Structure

```
src/nodo/interface_adapters/
└── __init__.py  # Currently empty
```

## Next Steps

- [Infrastructure](infrastructure.md) - See how adapters are wired together
- [Application Layer](application.md) - Review the interfaces being implemented

