# Project Structure

## Directory Layout

```
nodo/
├── src/
│   └── nodo/
│       ├── domain/                          # Layer 1: Business rules
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   ├── download.py
│       │   │   ├── torrent_search_result.py
│       │   │   └── user_preferences.py
│       │   ├── value_objects/
│       │   │   ├── __init__.py
│       │   │   ├── magnet_link.py
│       │   │   ├── file_size.py
│       │   │   ├── aggregator_source.py
│       │   │   ├── download_status.py
│       │   │   └── time_duration.py
│       │   └── exceptions/
│       │       ├── __init__.py
│       │       ├── domain_exception.py
│       │       ├── validation_error.py
│       │       ├── download_not_found_error.py
│       │       ├── duplicate_download_error.py
│       │       ├── invalid_state_transition_error.py
│       │       ├── torrent_client_error.py
│       │       ├── aggregator_error.py
│       │       ├── aggregator_timeout_error.py
│       │       └── file_system_error.py
│       ├── application/                     # Layer 2: Use cases
│       │   ├── interfaces/
│       │   │   ├── __init__.py
│       │   │   ├── download_repository.py
│       │   │   ├── user_preferences_repository.py
│       │   │   ├── aggregator_service.py
│       │   │   ├── aggregator_service_registry.py
│       │   │   └── torrent_client.py
│       │   ├── dtos/
│       │   │   ├── __init__.py
│       │   │   ├── download_dto.py
│       │   │   └── torrent_search_result_dto.py
│       │   └── use_cases/
│       │       ├── __init__.py
│       │       ├── search_torrents.py
│       │       ├── add_download.py
│       │       ├── list_downloads.py
│       │       ├── get_download_status.py
│       │       ├── get_user_preferences.py
│       │       ├── update_user_preferences.py
│       │       ├── add_favorite_path.py
│       │       ├── remove_favorite_path.py
│       │       ├── add_favorite_aggregator.py
│       │       └── remove_favorite_aggregator.py
│       ├── interface_adapters/              # Layer 3: Adapters (to be implemented)
│       │   └── __init__.py
│       └── infrastructure/                  # Layer 4: Frameworks (to be implemented)
│           ├── documentation/
│           │   ├── __init__.py
│           │   └── main.py
│           └── __init__.py
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── test_entities.py
│   │   │   └── test_value_objects.py
│   │   ├── application/
│   │   │   └── test_use_cases.py
│   │   ├── interface_adapters/
│   │   │   ├── test_repositories.py
│   │   │   ├── test_torrent_clients.py
│   │   │   └── test_aggregators.py
│   │   └── infrastructure/
│   │       ├── test_controllers.py
│   │       └── test_cli_commands.py
│   ├── integration/
│   │   └── test_end_to_end.py
│   └── conftest.py
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── LAYERS.md
│   │   ├── DOMAIN.md
│   │   ├── USE_CASES.md
│   │   ├── DEPENDENCY_INJECTION.md
│   │   └── PROJECT_STRUCTURE.md
│   ├── development/
│   │   ├── TESTING.md
│   │   ├── CODE_QUALITY.md
│   │   └── TECH_STACK.md
│   ├── user-guide/
│   │   ├── searching.md
│   │   ├── downloading.md
│   │   └── preferences.md
│   └── api-reference/
│       ├── domain.md
│       └── application.md
├── pyproject.toml
├── mkdocs.yml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── .gitignore
└── .env.example
```

---

## Layer Responsibilities

### Domain Layer (`src/nodo/domain/`)

**Purpose:** Core business logic, no external dependencies

**Contains:**
- `entities/` - Business objects (Download, TorrentSearchResult, UserPreferences)
- `value_objects/` - Immutable values (MagnetLink, FileSize, AggregatorSource, DownloadState, TimeDuration)
- `entities/` - Also includes DownloadStatus entity (status information from torrent client)
- `exceptions/` - Domain exceptions (DomainError, ValidationError, etc.)

**Rules:**
- ❌ No imports from other layers
- ❌ No external library dependencies
- ✅ Pure Python + standard library
- ✅ Most stable code

---

### Application Layer (`src/nodo/application/`)

**Purpose:** Use cases and application logic

**Contains:**
- `interfaces/` - Repository and service interfaces (ABC)
- `dtos/` - Data transfer objects
- `use_cases/` - Business workflows (10 use cases implemented)

**Rules:**
- ❌ No knowledge of frameworks or databases
- ✅ Depends only on domain layer
- ✅ Defines interfaces (ABC) for repositories and services
- ✅ Use cases define Input/Output as inner dataclasses

---

### Interface Adapters (`src/nodo/interface_adapters/`)

**Purpose:** Translate between domain and external world

**Contains:**
- (To be implemented) - Repository implementations, service adapters, protocols

**Status:** Currently empty (only `__init__.py`)

**Planned:**
- `protocols/` - Contracts for external libraries (Protocol)
- `repositories/` - Database implementations (SQLAlchemy)
- `torrent_clients/` - Torrent client adapters (qBittorrent)
- `aggregators/` - Torrent search adapters

**Rules:**
- ✅ Implements application layer interfaces (ABC)
- ✅ Receives dependencies via Protocols
- ❌ No CLI code
- ❌ No dependency injection logic

---

### Infrastructure Layer (`src/nodo/infrastructure/`)

**Purpose:** Frameworks, tools, and composition

**Contains:**
- `documentation/` - Documentation server (MkDocs helper)

**Status:** Minimal implementation (only documentation module)

**Planned:**
- `cli/` - Typer commands and routing
- `controllers/` - Presentation-agnostic controllers
- `config/` - Configuration management
- `di/` - Dependency injection container

**Rules:**
- ✅ Only place creating concrete objects
- ✅ Wires all dependencies together
- ✅ All framework-specific code

---

## Testing Structure

### Unit Tests (`tests/unit/`)

**Test each layer in isolation:**

```
tests/unit/
├── domain/
│   ├── test_download_entity.py
│   ├── test_user_preferences_entity.py
│   ├── test_magnet_link.py
│   └── test_file_size.py
├── application/
│   ├── test_search_torrents_use_case.py
│   ├── test_add_download_use_case.py
│   └── ...
├── interface_adapters/
│   ├── test_sqlite_download_repository.py
│   ├── test_qbittorrent_client.py
│   └── test_torrent_search_aggregator.py
└── infrastructure/
    ├── test_search_controller.py
    └── test_cli_commands.py
```

### Integration Tests (`tests/integration/`)

**Test full workflows:**

```
tests/integration/
├── test_search_and_add_workflow.py
├── test_download_management_workflow.py
└── test_preferences_workflow.py
```

---

## Documentation Structure

### Architecture Docs (`docs/architecture/`)

**Technical design documentation:**

- `LAYERS.md` - Clean Architecture layers
- `DOMAIN.md` - Entities and value objects
- `USE_CASES.md` - All 14 use cases
- `DEPENDENCY_INJECTION.md` - DI patterns
- `PROJECT_STRUCTURE.md` - This file

### Development Docs (`docs/development/`)

**Developer guides:**

- `TESTING.md` - Testing strategy and requirements
- `CODE_QUALITY.md` - Ruff, type hints, docstrings
- `TECH_STACK.md` - Technologies and dependencies

### User Docs (`docs/user-guide/`)

**End-user documentation:**

- `searching.md` - How to search torrents
- `downloading.md` - Managing downloads
- `preferences.md` - Configuring preferences

---

## Configuration Files

### `pyproject.toml`

**Project metadata and dependencies:**

```toml
[project]
name = "nodo"
version = "0.3.0"
requires-python = ">=3.13"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "pytest-cov>=7.0.0",
    "ruff>=0.14.8",
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.5.0",
    "mkdocstrings[python]>=0.24.0",
]

[tool.ruff]
line-length = 88
```

### `mkdocs.yml`

**Documentation site configuration:**

```yaml
site_name: Torrent CLI Manager
theme: material
plugins:
  - search
  - mkdocstrings
nav:
  - Home: index.md
  - Architecture: architecture/
  - Development: development/
```

### `.gitignore`

```
__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.coverage
htmlcov/
*.db
.env
```

---

## Entry Points

### CLI Entry Point

**Main entry:** (To be implemented) `src/nodo/infrastructure/cli/main.py`

**Documentation entry:** `src/nodo/infrastructure/documentation/main.py`

```python
# Documentation server entry point
def main():
    """Serve MkDocs documentation."""
    import subprocess
    subprocess.run(["mkdocs", "serve"])
```

### Installation

```toml
[project.scripts]
nodo-docs = "nodo.infrastructure.documentation.main:main"
```

---

## Import Guidelines

### ✅ Allowed Imports

```python
# Domain imports from nowhere
# (only standard library)

# Application imports from domain
from nodo.domain.entities.download import Download
from nodo.domain.value_objects import MagnetLink, FileSize
from nodo.application.interfaces.download_repository import IDownloadRepository

# Interface Adapters import from domain + application
from nodo.domain.entities.download import Download
from nodo.application.interfaces.download_repository import IDownloadRepository
# (Protocols to be defined when implemented)

# Infrastructure imports from anywhere
from nodo.application.use_cases.add_download import AddDownload
# (Repository implementations to be imported when implemented)
```

### ❌ Forbidden Imports

```python
# Domain CANNOT import from application
from nodo.application.use_cases.add_download import AddDownload  # NO!

# Application CANNOT import from interface_adapters
# (Will fail when interface_adapters are implemented)

# Application CANNOT import from infrastructure
# (Will fail when infrastructure is implemented)
```

---

## File Naming Conventions

- **Modules:** `snake_case.py`
- **Classes:** `PascalCase`
- **Tests:** `test_<module_name>.py`
- **Interfaces:** Prefix with `I` (e.g., `IDownloadRepository`)
- **Use Cases:** No suffix (e.g., `AddDownload`, not `AddDownloadUseCase`)

---

## Summary

**Four layers, strict dependencies:**
```
Domain → (no dependencies)
Application → Domain
Interface Adapters → Domain + Application
Infrastructure → All layers
```

**Testing mirrors source structure:**
```
tests/unit/<layer>/ corresponds to src/<layer>/
```

**Documentation explains:**
- Architecture (technical design)
- Development (how to contribute)
- User guide (how to use)
