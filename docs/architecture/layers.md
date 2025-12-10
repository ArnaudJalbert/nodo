# Clean Architecture Layers

## Overview

Four concentric layers with strict dependency rules: **Domain → Application → Interface Adapters → Infrastructure**

**Dependency Rule:** Outer layers depend on inner layers, never the reverse.

---

## Layer 1: Domain (Entities)

**Purpose:** Enterprise-wide business rules and core business objects.

**Characteristics:**
- ❌ No dependencies on other layers
- ❌ No external library dependencies (except standard library)
- ✅ Pure business logic and rules
- ✅ Most stable layer - rarely changes

**Contains:**
- Entities (Download, TorrentSearchResult, UserPreferences)
- Value Objects (MagnetLink, FileSize, FilePath, AggregatorSource)
- Domain exceptions
- Business rule validation

**Example:**
```python
# src/nodo/domain/entities/download.py
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from nodo.domain.value_objects import (
    AggregatorSource,
    DownloadState,
    FileSize,
    MagnetLink,
)

@dataclass(slots=True, kw_only=True)
class Download:
    """Core business entity - no external dependencies"""
    magnet_link: MagnetLink
    title: str
    file_path: Path
    source: AggregatorSource
    size: FileSize
    id_: UUID = field(default_factory=uuid4)
    status: DownloadState = DownloadState.DOWNLOADING
    date_added: datetime = field(default_factory=datetime.now)
    date_completed: datetime | None = None
```

---

## Layer 2: Application (Use Cases)

**Purpose:** Application-specific business rules and orchestration.

**Characteristics:**
- ❌ No knowledge of external agencies (DB, UI, frameworks)
- ❌ Does NOT implement repository interfaces (defines them)
- ✅ Defines interfaces (ABC) for repositories and services
- ✅ Contains use cases that orchestrate business logic
- ✅ Uses DTOs for input/output
- ✅ Depends only on domain layer

**Contains:**
- Use case classes
- Repository interfaces (ABC) - IDownloadRepository, IUserPreferencesRepository
- Service interfaces (ABC) - IAggregatorService, ITorrentClient
- DTOs (InputData, OutputData as inner classes)
- Application exceptions

**Example:**
```python
# src/nodo/application/interfaces/download_repository.py
from abc import ABC, abstractmethod
from uuid import UUID

from nodo.domain.entities import Download
from nodo.domain.value_objects import DownloadState, MagnetLink

class IDownloadRepository(ABC):
    """Interface defined in application layer"""
    @abstractmethod
    def save(self, download: Download) -> None:
        pass

# src/nodo/application/use_cases/add_download.py
from dataclasses import dataclass

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import IDownloadRepository, ITorrentClient

class AddDownload:
    """Use case depends on abstractions, not implementations"""
    
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
        download_repository: IDownloadRepository,  # ABC interface
        torrent_client: ITorrentClient             # ABC interface
    ):
        self._download_repository = download_repository
        self._torrent_client = torrent_client
    
    def execute(self, input_data: Input) -> Output:
        # Business logic here
        pass
```

---

## Layer 3: Interface Adapters (Adapters)

**Purpose:** Convert data between use cases and external agencies.

**Characteristics:**
- ✅ Implements application layer interfaces (ABC)
- ✅ Receives external dependencies via Protocol-typed constructors
- ✅ Contains all data format conversion
- ✅ Defines Protocols for external libraries
- ❌ No CLI code, no DI, no framework setup
- ❌ No knowledge of infrastructure layer

**Contains:**
- Protocols (typing.Protocol) - Define contracts for external libraries
- Repository implementations (SQLAlchemy)
- External service adapters (qBittorrent, torrent search)
- Data converters (domain ↔ external format)

**Example (Planned Implementation):**
```python
# src/nodo/interface_adapters/protocols/qbittorrent_protocol.py
from typing import Protocol

class QBittorrentClientProtocol(Protocol):
    """Protocol for external qbittorrent-api Client"""
    def torrents_add(self, urls: str, save_path: str) -> str: ...
    def torrents_info(self, torrent_hashes: str) -> list[dict]: ...

# src/nodo/interface_adapters/torrent_clients/qbittorrent_client.py
from nodo.application.interfaces.torrent_client import ITorrentClient
from nodo.domain.value_objects import MagnetLink

class QBittorrentClient(ITorrentClient):
    """Implements application interface, receives protocol-typed dependency"""
    
    def __init__(self, client: QBittorrentClientProtocol):
        """Inject external client via Protocol"""
        self.client = client
    
    def add_torrent(self, magnet_link: MagnetLink, download_path: str) -> str:
        # Convert domain objects to external format
        result = self.client.torrents_add(
            urls=str(magnet_link),
            save_path=download_path
        )
        return self._extract_torrent_id(result)
```

**Note:** Interface adapters are currently empty and will be implemented in future work.

---

## Layer 4: Infrastructure (Frameworks & Drivers)

**Purpose:** Outermost layer with frameworks, tools, and composition.

**Characteristics:**
- ✅ Only place where concrete external objects are created
- ✅ Wires up all dependencies (Composition Root)
- ✅ Contains all framework-specific code
- ✅ CLI framework (Typer)
- ✅ Controllers (presentation-agnostic)
- ✅ Configuration management

**Contains:**
- CLI commands (Typer) - Routing, parsing, formatting
- Controllers - Convert between CLI and use cases
- Request/Response models (Pydantic)
- Dependency injection container
- Configuration loading
- Framework glue code

**Example (Planned Implementation):**
```python
# src/nodo/infrastructure/di/container.py
import qbittorrentapi
from nodo.interface_adapters.torrent_clients.qbittorrent_client import QBittorrentClient
from nodo.application.interfaces import ITorrentClient
from nodo.application.use_cases.add_download import AddDownload

class Container:
    """Composition root - creates and wires all dependencies"""
    
    def torrent_client(self) -> ITorrentClient:
        # Create concrete external library object
        qbt = qbittorrentapi.Client(
            host=self.config.qbt_host,
            port=self.config.qbt_port
        )
        qbt.auth_log_in()
        
        # Inject into interface adapter
        return QBittorrentClient(client=qbt)
    
    def add_download_use_case(self) -> AddDownload:
        # Inject implementations (as interfaces)
        return AddDownload(
            download_repository=self.download_repository(),
            torrent_client=self.torrent_client()
        )

# src/nodo/infrastructure/cli/commands/download.py (to be implemented)
import typer
from nodo.application.use_cases.add_download import AddDownload

@app.command("add")
def add_download(magnet_link: str, title: str, ...):
    """CLI command - thin routing + formatting layer"""
    use_case = container.add_download_use_case()
    
    input_data = AddDownload.Input(
        magnet_link=magnet_link,
        title=title,
        ...
    )
    
    output = use_case.execute(input_data)
    
    # Format and display with Rich
    console.print(f"[green]✓[/green] Download added: {output.download.title}")
```

**Note:** Infrastructure layer currently only contains documentation server. CLI and DI container are pending implementation.

---

## Dependency Flow

```
Infrastructure (Frameworks, CLI, DI)
    ↓ depends on
Interface Adapters (Repositories, External Services)
    ↓ depends on
Application (Use Cases, Interfaces)
    ↓ depends on
Domain (Entities, Value Objects)
```

**Key Rule:** Inner layers never know about outer layers.

---

## Three Levels of Abstraction

1. **Domain Interfaces (ABC)** - Used by application layer
   - `IDownloadRepository`, `ITorrentClient`
   
2. **Interface Adapter Protocols (Protocol)** - Contract for external libraries
   - `QBittorrentClientProtocol`, `SQLAlchemyProtocol`
   
3. **Concrete Implementations** - Created only in infrastructure
   - `qbittorrentapi.Client`, `sqlalchemy.Engine`

---

## Testing Strategy by Layer

| Layer | Test Approach | Mock Type |
|-------|--------------|-----------|
| Domain | Pure unit tests | No mocks needed |
| Application | Mock interfaces | `Mock(spec=ABC)` |
| Interface Adapters | Mock protocols | `Mock(spec=Protocol)` |
| Infrastructure | Integration tests | Real or mock as needed |

---

## Common Violations to Avoid

❌ **Domain layer importing from application**
```python
# WRONG - domain importing application
from nodo.application.use_cases.add_download import AddDownload
```

❌ **Application layer importing concrete implementations**
```python
# WRONG - application importing adapter (will fail when adapters are implemented)
from nodo.interface_adapters.repositories.sqlite_repository import SQLiteRepository
```

❌ **Use case instantiating dependencies**
```python
# WRONG - use case creating its own dependencies
class AddDownload:
    def __init__(self):
        self.repository = SQLiteRepository()  # No!
```

✅ **Correct - dependency injection via interfaces**
```python
# CORRECT - use case receives interface
from nodo.application.interfaces.download_repository import IDownloadRepository

class AddDownload:
    def __init__(self, download_repository: IDownloadRepository):
        self._download_repository = download_repository
```

---

## Summary

- **Domain** - Business rules, no dependencies
- **Application** - Use cases + interfaces (ABC), orchestrates domain
- **Interface Adapters** - Implements interfaces, uses protocols, converts data
- **Infrastructure** - Frameworks, DI, composition root

**Always inject down, never instantiate.**