# Architecture Overview

Nodo is built using **Clean Architecture** principles, which ensures separation of concerns, testability, and maintainability. The architecture is organized into four distinct layers, each with specific responsibilities and dependencies.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                   Infrastructure                         │
│  (CLI, Dependency Injection, Configuration)             │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Interface Adapters                         │
│  (Repository Implementations, Service Adapters)         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Application                            │
│  (Use Cases, Interfaces/ABCs, DTOs)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Domain                               │
│  (Entities, Value Objects, Business Rules)              │
└─────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Domain Layer

The **innermost layer** containing the core business logic.

- **Entities**: Core business objects (`Download`, `TorrentSearchResult`, `UserPreferences`)
- **Value Objects**: Immutable objects representing domain concepts (`MagnetLink`, `FileSize`, `DownloadStatus`, `IndexerSource`)
- **Exceptions**: Domain-specific exceptions
- **No external dependencies**: Pure Python, standard library only

**Key Principle**: This layer is independent of all other layers and frameworks.

### Application Layer

Contains application-specific business rules and use cases.

- **Interfaces (ABCs)**: Abstract base classes defining contracts for external services
  - `IDownloadRepository` - Download persistence
  - `IUserPreferencesRepository` - Preferences persistence
  - `IndexerManager` - Indexer manager services (e.g., Prowlarr)
  - `ITorrentClient` - Torrent client operations
- **DTOs**: Data transfer objects for cross-layer communication
- **Use Cases**: Application-specific business logic (to be implemented)

**Key Principle**: Depends only on the Domain layer. Defines interfaces, not implementations.

### Interface Adapters Layer

Implements the interfaces defined in the Application layer.

- **Repository Implementations**: Concrete implementations of repository interfaces
  - `SQLiteDownloadRepository`
  - `SQLiteUserPreferencesRepository`
- **Service Adapters**: Adapters for external services
  - `QBittorrentAdapter` - qBittorrent client integration
  - `ProwlarrIndexerManager` - Prowlarr indexer manager adapter
  - `IProwlarrSource` - Protocol for Prowlarr API integration

**Key Principle**: Implements Application layer interfaces, depends on Domain and Application layers.

### Infrastructure Layer

The outermost layer containing framework and glue code.

- **CLI**: Command-line interface using Typer
- **Dependency Injection**: Container setup and factory functions
- **Configuration**: Configuration management (TOML/YAML)
- **Database**: SQLAlchemy models and migrations
- **Indexers**: Prowlarr adapter for indexer API integration

**Key Principle**: Depends on all inner layers. Contains framework-specific code.

## Dependency Rule

The **Dependency Rule** is fundamental to Clean Architecture:

> Source code dependencies can only point inward. Nothing in an inner layer can know anything about an outer layer.

This means:
- ✅ Domain can depend on nothing
- ✅ Application can depend on Domain
- ✅ Interface Adapters can depend on Application and Domain
- ✅ Infrastructure can depend on all layers

## Benefits

This architecture provides:

1. **Independence**: Business logic is independent of frameworks, databases, and UI
2. **Testability**: Each layer can be tested in isolation
3. **Flexibility**: Easy to swap implementations (e.g., switch from SQLite to PostgreSQL)
4. **Maintainability**: Clear separation of concerns makes code easier to understand and modify

## Project Structure

```
src/nodo/
├── domain/              # Domain layer
│   ├── entities/        # Business entities
│   ├── value_objects/   # Value objects
│   └── exceptions/      # Domain exceptions
├── application/         # Application layer
│   ├── interfaces/      # Abstract interfaces (ABCs)
│   └── dtos/           # Data transfer objects
├── interface_adapters/  # Interface Adapters layer
│   └── (implementations)
└── infrastructure/      # Infrastructure layer
    └── (CLI, DI, config)
```

## Further Reading

- [Domain Layer](domain.md) - Deep dive into domain entities and value objects
- [Application Layer](application.md) - Use cases and interfaces
- [Interface Adapters](interface-adapters.md) - Repository and service implementations
- [Infrastructure](infrastructure.md) - CLI and framework code

