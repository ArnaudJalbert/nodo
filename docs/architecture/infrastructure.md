# Infrastructure Layer

The Infrastructure layer is the **outermost layer** containing framework-specific code, dependency injection, and the entry point of the application.

## Principles

- ✅ **Depends on all inner layers** - Can use Domain, Application, and Interface Adapters
- ✅ **Framework-specific code** - CLI, web framework, etc.
- ✅ **Dependency injection** - Wires together all components
- ✅ **Configuration management** - Handles environment variables, config files

## Components

### CLI (Command-Line Interface)

The CLI is built using [Typer](https://typer.tiangolo.com/) and provides the user-facing interface.

**Commands:**
- `search` - Search for torrents across aggregators
- `add` - Add a new download
- `list` - List all downloads
- `status` - Show download status
- `pause` - Pause a download
- `resume` - Resume a paused download
- `remove` - Remove a download
- `config` - Manage user preferences

**Location**: `src/nodo/infrastructure/cli/` (to be implemented)

**Example Structure:**
```python
import typer

app = typer.Typer()

@app.command()
def search(query: str) -> None:
    """Search for torrents."""
    # Get use case from DI container
    search_use_case = container.get(SearchTorrents)
    
    # Execute use case
    results = search_use_case.execute(query)
    
    # Display results
    display_results(results)
```

### Dependency Injection

The DI container wires together all components, providing implementations to use cases.

**Responsibilities:**
- Create repository instances
- Create service adapter instances
- Create use case instances with dependencies
- Manage singleton instances (e.g., database session)

**Location**: `src/nodo/infrastructure/di/` (to be implemented)

**Example Structure:**
```python
class Container:
    def __init__(self):
        # Create database session
        self._session = create_session()
        
        # Create repositories
        self._download_repo = SQLiteDownloadRepository(self._session)
        self._preferences_repo = SQLiteUserPreferencesRepository(self._session)
        
        # Create service adapters
        self._torrent_client = QBittorrentAdapter(...)
        self._aggregators = [
            The1337xAdapter(),
            ThePirateBayAdapter()
        ]
        
        # Create use cases
        self._add_download = AddDownload(
            self._download_repo,
            self._torrent_client,
            self._preferences_repo
        )
    
    def get(self, use_case_type: type) -> Any:
        # Return use case instance
        pass
```

### Configuration Management

Handles loading and managing configuration from files and environment variables.

**Configuration Sources:**
- `~/.config/nodo/config.toml` - User configuration file
- Environment variables - Override file settings
- Default values - Fallback when not configured

**Configuration Options:**
- `download_path` - Default download directory
- `max_concurrent_downloads` - Maximum concurrent downloads
- `auto_start_downloads` - Whether to auto-start downloads
- `qbittorrent_url` - qBittorrent Web UI URL
- `qbittorrent_username` - qBittorrent username
- `qbittorrent_password` - qBittorrent password
- `database_path` - SQLite database path

**Location**: `src/nodo/infrastructure/config/` (to be implemented)

**Example Structure:**
```python
@dataclass
class Config:
    download_path: Path
    max_concurrent_downloads: int
    auto_start_downloads: bool
    qbittorrent_url: str
    qbittorrent_username: str
    qbittorrent_password: str
    database_path: Path

def load_config() -> Config:
    # Load from file
    # Override with environment variables
    # Apply defaults
    pass
```

### Database Setup

Handles database initialization, migrations, and connection management.

**Responsibilities:**
- Create database if it doesn't exist
- Run migrations (if using Alembic)
- Create SQLAlchemy session factory
- Handle database connection errors

**Location**: `src/nodo/infrastructure/database/` (to be implemented)

### Error Handling

Infrastructure layer handles:

- CLI error display
- Logging configuration
- Global exception handlers
- User-friendly error messages

## Application Entry Point

The main entry point initializes the infrastructure and starts the CLI:

```python
# src/nodo/infrastructure/__main__.py
def main():
    # Load configuration
    config = load_config()
    
    # Initialize DI container
    container = Container(config)
    
    # Run CLI
    cli_app(container)
```

## Testing

Infrastructure layer can be tested with:

- **End-to-end tests** - Full CLI command execution
- **Integration tests** - With real database and services
- **Unit tests** - Individual components with mocks

## Project Structure

```
src/nodo/infrastructure/
├── cli/
│   └── commands.py          # CLI command definitions
├── di/
│   └── container.py         # Dependency injection container
├── config/
│   └── loader.py            # Configuration loading
├── database/
│   └── setup.py             # Database initialization
└── __main__.py              # Application entry point
```

## Next Steps

- [Architecture Overview](overview.md) - Review the complete architecture
- [Development Guide](../development/setup.md) - Learn how to set up the development environment

