# Dependency Injection with Protocols

## Three Levels of Abstraction

**Protocol-based DI enables testable, loosely-coupled code:**

1. **Domain Interfaces (ABC)** - Used by application layer
2. **Interface Adapter Protocols (Protocol)** - Contracts for external libraries
3. **Concrete Implementations** - Created only in infrastructure

---

## Why Protocols?

**Protocols enable testing interface adapters WITHOUT external dependencies.**

### Benefits

✅ **Interface adapters are testable in isolation**
- Test `QBittorrentClient` without installing qBittorrent
- Use `Mock(spec=Protocol)` in tests

✅ **Easy to swap external libraries**
- Want to switch torrent clients?
- Create new protocol, implement adapter, inject at composition root
- Use cases don't change

✅ **Clear contracts**
- Protocol explicitly defines required methods
- IDE autocomplete and type checking work perfectly

✅ **No coupling to implementation details**
- Tests depend on protocols, not concrete libraries
- More maintainable test suite

---

## Pattern: Three-Layer Abstraction

### Level 1: Domain Interface (ABC)

**Location:** `src/domain/services/torrent_client.py`

```python
from abc import ABC, abstractmethod

class ITorrentClient(ABC):
    """Domain interface - used by application layer use cases"""
    
    @abstractmethod
    def add_torrent(self, magnet_link: MagnetLink, download_path: FilePath) -> str:
        """Add torrent and return torrent_id"""
        pass
    
    @abstractmethod
    def get_torrent_status(self, torrent_id: str) -> dict:
        """Get current status and progress"""
        pass
    
    @abstractmethod
    def pause_torrent(self, torrent_id: str) -> bool:
        """Pause a torrent"""
        pass
```

### Level 2: Interface Adapter Protocol

**Location:** `src/interface_adapters/protocols/qbittorrent_protocol.py`

```python
from typing import Protocol

class QBittorrentClientProtocol(Protocol):
    """
    Protocol for the external qbittorrent-api Client object.
    
    This defines the contract for what methods the external library
    must provide, allowing us to mock it in tests.
    """
    
    def torrents_add(self, urls: str, save_path: str) -> str:
        """Add torrent by magnet link"""
        ...
    
    def torrents_info(self, torrent_hashes: str) -> list[dict]:
        """Get torrent information"""
        ...
    
    def torrents_pause(self, torrent_hashes: str) -> None:
        """Pause torrents"""
        ...
    
    def torrents_resume(self, torrent_hashes: str) -> None:
        """Resume torrents"""
        ...
    
    def auth_log_in(self, username: str, password: str) -> None:
        """Authenticate with qBittorrent"""
        ...
```

### Level 3: Interface Adapter Implementation

**Location:** `src/interface_adapters/torrent_clients/qbittorrent_client.py`

```python
class QBittorrentClient(ITorrentClient):
    """
    Implements domain interface, receives external client via Protocol.
    
    This adapter translates between our domain interface (ITorrentClient)
    and the external library (qbittorrent-api).
    """
    
    def __init__(self, client: QBittorrentClientProtocol):
        """
        Inject the actual qbittorrent-api Client through protocol.
        
        This allows us to:
        1. Test with Mock(spec=QBittorrentClientProtocol)
        2. Swap out the external library if needed
        3. Type-check the external library's methods
        """
        self.client = client
    
    def add_torrent(self, magnet_link: MagnetLink, download_path: FilePath) -> str:
        """Implement domain interface using injected client"""
        result = self.client.torrents_add(
            urls=str(magnet_link),
            save_path=str(download_path)
        )
        return self._extract_torrent_id(result)
    
    def get_torrent_status(self, torrent_id: str) -> dict:
        """Implement domain interface using injected client"""
        torrents = self.client.torrents_info(torrent_hashes=torrent_id)
        if not torrents:
            raise TorrentClientError(f"Torrent {torrent_id} not found")
        
        torrent = torrents[0]
        return {
            'status': self._map_status(torrent['state']),
            'progress': torrent['progress'] * 100,
            'download_rate': torrent['dlspeed'],
            'upload_rate': torrent['upspeed'],
            'eta': torrent['eta']
        }
```

---

## Application Layer: Use Cases

**Use cases depend on domain interfaces (ABC), not implementations:**

```python
# src/application/use_cases/add_download.py

class AddDownloadUseCase:
    """Use case depends on abstractions, not concretions"""
    
    def __init__(
        self,
        repository: IDownloadRepository,      # ABC interface
        torrent_client: ITorrentClient,       # ABC interface
        preferences_repository: IUserPreferencesRepository  # ABC interface
    ):
        """Inject all dependencies via domain interfaces"""
        self.repository = repository
        self.torrent_client = torrent_client
        self.preferences_repository = preferences_repository
    
    def execute(self, input_data: InputData) -> OutputData:
        """Execute use case using injected dependencies"""
        # Business logic here - uses interfaces, not implementations
        pass
```

---

## Infrastructure Layer: Composition Root

**Only place where concrete objects are created:**

```python
# src/infrastructure/di/container.py

import qbittorrentapi
from sqlalchemy import create_engine

class Container:
    """Dependency injection container - composition root"""
    
    def __init__(self):
        self._config = Config.load()
    
    def torrent_client(self) -> ITorrentClient:
        """Factory method for torrent client"""
        # Create concrete external library object
        qbt = qbittorrentapi.Client(
            host=self._config.qbt_host,
            port=self._config.qbt_port,
            username=self._config.qbt_username,
            password=self._config.qbt_password
        )
        qbt.auth_log_in()
        
        # Inject into interface adapter
        # qbittorrentapi.Client satisfies QBittorrentClientProtocol
        return QBittorrentClient(client=qbt)
    
    def download_repository(self) -> IDownloadRepository:
        """Factory method for download repository"""
        engine = create_engine(f"sqlite:///{self._config.db_path}")
        session = Session(engine)
        return SQLiteDownloadRepository(session=session)
    
    def add_download_use_case(self) -> AddDownloadUseCase:
        """Factory method for use case with all dependencies"""
        return AddDownloadUseCase(
            repository=self.download_repository(),
            torrent_client=self.torrent_client(),
            preferences_repository=self.preferences_repository()
        )
```

---

## Testing: Mock with Protocols

### Testing Interface Adapters

**Use `Mock(spec=Protocol)` to test adapters:**

```python
from unittest.mock import Mock

def test_qbittorrent_client_add_torrent() -> None:
    """Test interface adapter implementation with mock protocol"""
    # Arrange - Mock external library using Protocol
    mock_client = Mock(spec=QBittorrentClientProtocol)
    mock_client.torrents_add.return_value = "abc123def456"
    
    qbt_client = QBittorrentClient(client=mock_client)
    
    magnet = MagnetLink.from_string("magnet:?xt=urn:btih:abc123...")
    path = FilePath("/downloads")
    
    # Act
    torrent_id = qbt_client.add_torrent(magnet, path)
    
    # Assert
    assert torrent_id == "abc123def456"
    mock_client.torrents_add.assert_called_once_with(
        urls=str(magnet),
        save_path=str(path)
    )
```

### Testing Use Cases

**Use `Mock(spec=Interface)` to test use cases:**

```python
def test_add_download_use_case() -> None:
    """Test use case with mocked domain interfaces"""
    # Arrange - Mock domain interfaces (ABC)
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists.return_value = False
    
    mock_client = Mock(spec=ITorrentClient)
    mock_client.add_torrent.return_value = "torrent_123"
    
    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()
    
    use_case = AddDownloadUseCase(
        repository=mock_repo,
        torrent_client=mock_client,
        preferences_repository=mock_prefs_repo
    )
    
    input_data = AddDownloadUseCase.InputData(
        magnet_link="magnet:?xt=urn:btih:abc123...",
        title="Test",
        source="1337x",
        size="1.5 GB"
    )
    
    # Act
    result = use_case.execute(input_data)
    
    # Assert
    assert result.download.status == "DOWNLOADING"
    mock_repo.exists.assert_called_once()
    mock_client.add_torrent.assert_called_once()
```

---

## Key Principles

### 1. Never Import Concrete Implementations

❌ **Wrong - use case importing adapter:**
```python
from src.interface_adapters.torrent_clients.qbittorrent_client import QBittorrentClient

class AddDownloadUseCase:
    def __init__(self):
        self.client = QBittorrentClient()  # NO!
```

✅ **Correct - use case depends on interface:**
```python
from src.domain.services.torrent_client import ITorrentClient

class AddDownloadUseCase:
    def __init__(self, torrent_client: ITorrentClient):
        self.torrent_client = torrent_client  # YES!
```

### 2. Inject All Dependencies Via Constructor

✅ **Every layer receives dependencies via constructor:**

```python
# Use Case receives domain interfaces
def __init__(self, repository: IRepository, client: IClient):
    ...

# Interface Adapter receives protocol-typed external dependencies
def __init__(self, client: QBittorrentClientProtocol):
    ...
```

### 3. Composition Happens Only in Infrastructure

**DI Container is the ONLY place creating concrete objects:**

```python
# Infrastructure layer - ONLY place creating concrete objects
qbt = qbittorrentapi.Client(...)      # Create external library object
client = QBittorrentClient(client=qbt)  # Inject into adapter
use_case = AddDownloadUseCase(torrent_client=client)  # Inject into use case
```

---

## Benefits Summary

✅ **Testability** - Mock at every level with type safety
✅ **Flexibility** - Swap implementations without changing use cases
✅ **Type Safety** - Protocols ensure external libraries match contracts
✅ **Maintainability** - Clear dependencies, easy to understand
✅ **Isolation** - Test each layer independently

---

## Common Patterns

### Repository with Session Protocol

```python
# Protocol
class SessionProtocol(Protocol):
    def add(self, instance: object) -> None: ...
    def commit(self) -> None: ...
    def query(self, *entities): ...

# Implementation
class SQLiteDownloadRepository(IDownloadRepository):
    def __init__(self, session: SessionProtocol):
        self.session = session
    
    def save(self, download: Download) -> Download:
        # Use session via protocol
        self.session.add(download_model)
        self.session.commit()
        return download
```

### Service with HTTP Client Protocol

```python
# Protocol
class HTTPClientProtocol(Protocol):
    def get(self, url: str, **kwargs) -> dict: ...
    def post(self, url: str, **kwargs) -> dict: ...

# Implementation
class TorrentSearchAggregator(IAggregatorService):
    def __init__(self, http_client: HTTPClientProtocol):
        self.http_client = http_client
    
    def search(self, query: str) -> list[TorrentSearchResult]:
        response = self.http_client.get(url, params={'q': query})
        return self._parse_results(response)
```

---

## Summary

- **Three abstraction levels:** Domain Interface (ABC) → Protocol → Concrete
- **Use cases depend on ABC interfaces**
- **Adapters depend on Protocols**
- **Infrastructure creates concrete objects**
- **Test with `Mock(spec=Protocol)` or `Mock(spec=ABC)`**
- **Never instantiate dependencies inside use cases/adapters**

**Inject all the way down. Compose only at the top.**