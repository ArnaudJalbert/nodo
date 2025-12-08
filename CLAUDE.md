# CLI Torrent Download Manager - Domain Design

## Clean Architecture Principles

Your goal is to produce code that follows **Robert C. Martin's Clean Architecture** and the layers we decided to implement.

---

### Layer Definitions

#### 📦 `domain` Layer - Entities

**Purpose:** Encapsulate Enterprise-wide business rules.

An entity can be an object with methods, or it can be a set of data structures and functions. It doesn't matter so long as the entities could be used by many different applications in the enterprise.

If you don't have an enterprise, and are just writing a single application, then these entities are the business objects of the application. They encapsulate the most general and high-level rules. They are the least likely to change when something external changes.

**Key Points:**
- ❌ No dependencies on other layers
- ❌ No external library dependencies (except standard library)
- ✅ Pure business logic and rules
- ✅ Most stable layer - rarely changes

**Examples:**
- You would NOT expect these objects to be affected by a change to page navigation or security
- No operational change to any particular application should affect the entity layer

---

#### 🎯 `application` Layer - Use Cases

**Purpose:** Contains application-specific business rules.

It encapsulates and implements all of the use cases of the system. These use cases orchestrate the flow of data to and from the entities, and direct those entities to use their enterprise-wide business rules to achieve the goals of the use case.

**Key Points:**
- ❌ We do NOT expect changes in this layer to affect the entities
- ❌ We do NOT expect this layer to be affected by changes to externalities (database, UI, frameworks)
- ✅ This layer is isolated from such concerns
- ✅ Defines interfaces (ABCs) for repositories and external services
- ✅ Use cases depend on these abstractions, not concrete implementations
- ✅ Changes when operation of the application changes

**What Lives Here:**
- Interfaces (ABCs) for repositories (IDownloadRepository, IUserPreferencesRepository)
- Interfaces (ABCs) for external services (IAggregatorService, ITorrentClient)
- Use cases that orchestrate business logic
- DTOs for input/output data transfer

**Examples:**
- If the details of a use-case change, then some code in this layer will certainly be affected
- Changes to the database or UI will NOT affect this layer

---

#### 🔌 `interface_adapters` Layer - Adapters

**Purpose:** Convert data between use cases/entities and external agencies.

The software in this layer is a set of adapters that convert data from the format most convenient for the use cases and entities, to the format most convenient for some external agency such as the Database or the Web.

**Key Points:**
- ✅ Contains all data format conversion
- ✅ Implements application layer interfaces (ABCs)
- ✅ Receives external dependencies via Protocol-typed constructors
- ✅ No CLI code, no DI, no framework setup
- ❌ No knowledge of infrastructure layer

**Examples:**
- **MVC Architecture:** Presenters, Views, and Controllers all belong here
- **Database:** All SQL should be restricted to this layer
- **External Services:** Adapters to convert data from external services to internal form

**What Lives Here:**
- Repository implementations (SQLAlchemy models, SQL queries)
- External service adapters (qBittorrent client, torrent search)
- Protocols defining contracts for external libraries
- Data conversion between domain and external formats

---

#### 🚀 `infrastructure` Layer - Frameworks & Drivers

**Purpose:** Outermost layer composed of frameworks and tools.

Generally you don't write much code in this layer other than glue code that communicates to the next circle inwards. This layer is where all the details go.

**Key Points:**
- ✅ The Web is a detail
- ✅ The database is a detail
- ✅ We keep these things on the outside where they can do little harm
- ✅ Only place where concrete external library objects are created
- ✅ Wires up all dependencies (Composition Root)

**What Lives Here:**
- CLI framework (Typer)
- Controllers (presentation-agnostic)
- Request/Response models (Pydantic)
- Dependency injection container
- Configuration management
- All framework-specific code

---

### 🧪 Testing Requirements

#### **100% Test Coverage Mandate**

Every piece of code written must have corresponding tests. This is **NON-NEGOTIABLE**.

**Coverage Requirements:**
- ✅ **Domain Layer:** 100% coverage - Pure logic, easy to test
- ✅ **Application Layer:** 100% coverage - Use Mock(spec=Interface)
- ✅ **Interface Adapters:** 100% coverage - Use Mock(spec=Protocol)
- ✅ **Infrastructure Layer:** 100% coverage - Integration tests where appropriate

**Testing Strategy by Layer:**

```
📦 Domain Layer Tests
├── Entities: Test all methods, business rules, validation
├── Value Objects: Test creation, validation, immutability
├── Interfaces: No implementation to test, but document expected behavior
└── Coverage: 100% - No exceptions

🎯 Application Layer Tests  
├── Use Cases: Mock all dependencies with Mock(spec=Interface)
├── Test all flows: happy path, error cases, edge cases
├── Test exception handling
└── Coverage: 100% - Every use case, every path

🔌 Interface Adapters Tests
├── Repositories: Mock protocols with Mock(spec=Protocol)
├── External Adapters: Mock external library clients
├── Test conversion logic between domain and external formats
└── Coverage: 100% - All adapters, all methods

🚀 Infrastructure Layer Tests
├── Controllers: Mock use cases, test Request/Response conversion
├── CLI Commands: Integration tests with real controllers (mocked use cases)
├── DI Container: Test wiring
└── Coverage: 100% - All user-facing code paths
```

**Test Style: Pytest Functions (NOT Classes)**

Use plain pytest functions, NOT test classes. This is the project standard.

```python
# ✅ CORRECT - Use plain functions
def test_magnet_link_extracts_info_hash() -> None:
    """Should extract info hash from magnet link."""
    magnet = MagnetLink(uri="magnet:?xt=urn:btih:abc123...")
    assert magnet.info_hash == "abc123..."

def test_magnet_link_rejects_invalid_uri() -> None:
    """Should reject invalid magnet URI."""
    with pytest.raises(ValidationError):
        MagnetLink(uri="invalid")

# ❌ WRONG - Do NOT use test classes
class TestMagnetLink:
    def test_extracts_info_hash(self) -> None:
        ...
```

**Test-Driven Development (TDD) Encouraged:**
1. ✅ Write test first (Red)
2. ✅ Write minimal code to pass (Green)
3. ✅ Refactor (Refactor)
4. ✅ Repeat

**When Adding Code:**
```
❌ DON'T: Write code without tests
❌ DON'T: Leave tests for later
❌ DON'T: Skip "trivial" code

✅ DO: Write test first or immediately after
✅ DO: Test all branches and edge cases
✅ DO: Run coverage report regularly
✅ DO: Aim for 100% coverage at all times
```

**Coverage Tools:**
```bash
# Install coverage tool
uv add --dev pytest pytest-cov

# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html

# Fail if coverage below 100%
pytest --cov=src --cov-fail-under=100
```

**No Excuses:**
- "It's just a simple getter" → **Test it**
- "It's just wiring code" → **Test it**  
- "It's hard to test" → **Refactor to make it testable**
- "I'll add tests later" → **NO. Add them NOW.**

---

### Code Quality Requirements

**Return Python 3.11+ compatible code with:**
- ✅ Correct type hints everywhere
- ✅ Proper docstrings (Google style)
- ✅ **Formatted with `ruff format`** (no exceptions)
- ✅ **Lint-free with `ruff check`** (must pass)
- ✅ 100% test coverage
- ✅ Clean Architecture principles followed

#### Ruff Configuration

**Install ruff:**
```bash
uv add --dev ruff
```

**Format all code:**
```bash
# Format code (automatic fixes)
ruff format .

# Check linting
ruff check .

# Auto-fix linting issues where possible
ruff check --fix .
```

**Pre-commit workflow:**
```bash
# Before every commit
ruff format .
ruff check --fix .
pytest --cov=src --cov-fail-under=100
```

**Configuration in `pyproject.toml`:**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Rules:**
- ❌ No code committed without running `ruff format`
- ❌ No code with `ruff check` errors
- ✅ All code must pass both checks
- ✅ Configure ruff in `pyproject.toml`

---

### 📚 Documentation Requirements

#### MkDocs Documentation

**As you build the application, build MkDocs documentation alongside it.**

**Install MkDocs:**
```bash
uv add --dev mkdocs mkdocs-material mkdocstrings[python]
```

**Structure:**
```
docs/
├── index.md                    # Overview
├── getting-started.md          # Installation & Quick Start
├── architecture/
│   ├── overview.md            # Clean Architecture explanation
│   ├── domain.md              # Domain layer details
│   ├── application.md         # Application layer details
│   ├── interface-adapters.md  # Interface adapters details
│   └── infrastructure.md      # Infrastructure details
├── user-guide/
│   ├── searching.md           # How to search torrents
│   ├── downloading.md         # Managing downloads
│   └── preferences.md         # Configuring preferences
├── api-reference/
│   ├── domain/                # Auto-generated from docstrings
│   ├── application/
│   ├── interface-adapters/
│   └── infrastructure/
└── contributing.md            # How to contribute
```

**MkDocs Configuration (`mkdocs.yml`):**
```yaml
site_name: Torrent CLI Manager
site_description: CLI-based torrent download manager following Clean Architecture
site_author: Your Name

theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - search.suggest

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Architecture:
      - Overview: architecture/overview.md
      - Domain Layer: architecture/domain.md
      - Application Layer: architecture/application.md
      - Interface Adapters: architecture/interface-adapters.md
      - Infrastructure Layer: architecture/infrastructure.md
  - User Guide:
      - Searching Torrents: user-guide/searching.md
      - Managing Downloads: user-guide/downloading.md
      - Preferences: user-guide/preferences.md
  - API Reference:
      - Domain: api-reference/domain.md
      - Application: api-reference/application.md
  - Contributing: contributing.md

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed
  - admonition
  - codehilite
```

**Build and serve:**
```bash
# Serve locally during development
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

**Documentation Rules:**
- ✅ Document as you code (not after)
- ✅ Every module needs docstrings (Google style)
- ✅ Architecture decisions go in `docs/architecture/`
- ✅ User-facing features go in `docs/user-guide/`
- ✅ Update docs when behavior changes

---

#### README.md

**Follow guidelines from [makeareadme.com](https://www.makeareadme.com/)**

**Required sections:**
```markdown
# Torrent CLI Manager

[Brief description - one paragraph]

## Features

- [Bullet list of key features]

## Installation

[Step-by-step installation instructions]

## Usage

[Basic usage examples with code blocks]

## Configuration

[How to configure the application]

## Documentation

Full documentation available at: [link to MkDocs site]

## Development

[How to set up development environment]

## Testing

[How to run tests]

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

[License information]

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
```

**Update README as you go:**
- ✅ Add features when implemented
- ✅ Update usage examples when CLI changes
- ✅ Keep installation instructions current
- ✅ Add screenshots/GIFs for visual features

---

#### CHANGELOG.md

**Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) guidelines.**

**Format:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features go here

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes

## [0.1.0] - 2025-01-15

### Added
- Initial release
- Domain layer with Download and UserPreferences entities
- 14 use cases for download and preferences management
- CLI interface with Typer
- SQLite storage with SQLAlchemy
- qBittorrent integration

[Unreleased]: https://github.com/username/torrent-cli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/username/torrent-cli/releases/tag/v0.1.0
```

**Changelog Rules:**
- ✅ Be concise - one line per change
- ✅ Group by category (Added, Changed, Fixed, etc.)
- ✅ Update on every significant change
- ✅ Keep Unreleased section at top
- ✅ Date format: YYYY-MM-DD
- ❌ Don't include internal refactoring
- ❌ Don't include typo fixes
- ✅ Include breaking changes prominently

---

#### CONTRIBUTING.md

**Required content:**

```markdown
# Contributing to Torrent CLI Manager

Thank you for your interest in contributing!

## Development Setup

### Prerequisites
- Python 3.11+
- UV package manager
- qBittorrent installed and running

### Setup Steps

1. Clone the repository
   ```bash
   git clone https://github.com/username/torrent-cli.git
   cd torrent-cli
   ```

2. Create virtual environment with UV
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   uv pip install -e ".[dev]"
   ```

4. Run tests
   ```bash
   pytest --cov=src --cov-fail-under=100
   ```

## Development Workflow

### Before Writing Code

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Read the architecture documentation in `docs/architecture/`

### Writing Code

1. **Follow Clean Architecture**
   - Domain → Application → Interface Adapters → Infrastructure
   - No circular dependencies
   - Depend on abstractions, not concretions

2. **Write tests FIRST or immediately after**
   - 100% coverage required
   - Use `Mock(spec=Protocol)` for testing
   - Test all edge cases

3. **Format and lint**
   ```bash
   ruff format .
   ruff check --fix .
   ```

4. **Run tests**
   ```bash
   pytest --cov=src --cov-fail-under=100
   ```

5. **Update documentation**
   - Add docstrings (Google style)
   - Update relevant docs in `docs/`
   - Update README if user-facing change
   - Update CHANGELOG.md

### Before Committing

Run this checklist:
```bash
# Format code
ruff format .

# Check linting
ruff check .

# Run tests with coverage
pytest --cov=src --cov-fail-under=100

# Type checking (optional but recommended)
mypy src/

# Build docs
mkdocs build
```

### Commit Messages

Follow conventional commits:
```
feat: add user preferences entity
fix: resolve duplicate download bug
docs: update architecture documentation
test: add tests for SearchTorrents use case
refactor: extract validation logic to value object
```

### Pull Request Process

1. Ensure all checks pass
2. Update CHANGELOG.md under `[Unreleased]`
3. Update README.md if needed
4. Request review
5. Address feedback
6. Squash commits before merge (if requested)

## Code Style

- **Line length:** 100 characters
- **Quotes:** Double quotes
- **Imports:** Sorted with isort (via ruff)
- **Type hints:** Required everywhere
- **Docstrings:** Google style, required for all public functions

## Testing Guidelines

- **Unit tests:** Test in isolation with mocks
- **Integration tests:** Test with real adapters
- **Test file naming:** `test_<module>.py`
- **Test function naming:** `test_<function>_<scenario>()`
- **Coverage:** 100% required, no exceptions

## Architecture Guidelines

### Domain Layer
- No external dependencies
- Pure business logic
- Value objects are immutable
- Entities contain business rules

### Application Layer
- Depends only on domain interfaces
- No knowledge of infrastructure
- Use cases orchestrate flow
- Return DTOs, not entities

### Interface Adapters
- Implement domain interfaces
- Use protocols for external dependencies
- Convert between formats
- No framework knowledge

### Infrastructure
- Framework-specific code
- Composition root
- Dependency injection
- CLI commands

## Questions?

- Open an issue for bugs
- Start a discussion for questions
- Read the docs at [link]

## Code of Conduct

Be respectful, inclusive, and professional.
```

---

### Documentation Workflow Summary

**For every feature added:**

1. ✅ **Write code** with proper docstrings
2. ✅ **Write tests** (100% coverage)
3. ✅ **Format & lint** (`ruff format` + `ruff check`)
4. ✅ **Update MkDocs** (`docs/` directory)
5. ✅ **Update README.md** (if user-facing)
6. ✅ **Update CHANGELOG.md** (concise entry)
7. ✅ **Build docs** (`mkdocs serve` to verify)
8. ✅ **Commit** with conventional commit message

**Documentation is not optional - it's part of the implementation.**

---

## Project Overview
A simple CLI-based torrent download manager that allows users to search for torrents via external aggregators and track downloaded files locally. Built using Clean Architecture principles.

## Core Requirements
- Search torrents from CLI
- Track downloaded files locally
- No user management (single-user, local tool)
- Keep architecture simple and maintainable

---

## Domain Entities

### 1. TorrentSearchResult (Ephemeral)
Represents a torrent found from an aggregator search. Not persisted long-term.

**Attributes:**
- `magnet_link`: string - Unique identifier for the torrent
- `title`: string - Name/title of the torrent
- `size`: string - File size (e.g., "1.5 GB")
- `seeders`: int - Number of seeders
- `leechers`: int - Number of leechers
- `source`: string - Which aggregator it came from (e.g., "1337x", "ThePirateBay")
- `date_found`: datetime - When this result was retrieved

**Notes:**
- This entity exists only in memory during search operations
- Not persisted to database
- Can be converted to a Download entity when user selects it

---

### 2. Download (Core Entity)
Represents a torrent that has been downloaded or is currently downloading. This is the main persisted entity.

**Attributes:**
- `id`: UUID - Unique identifier (primary key)
- `magnet_link`: string - The magnet link used to download
- `title`: string - Name of the downloaded content
- `file_path`: string - Local file system path where content is saved
- `source`: string - Which aggregator it was downloaded from
- `status`: enum - Current status of the download
  - `DOWNLOADING`
  - `COMPLETED`
  - `FAILED`
  - `PAUSED`
- `date_added`: datetime - When the download was initiated
- `date_completed`: datetime (nullable) - When the download finished
- `size`: string - Total size of the download

**Notes:**
- This is the source of truth for all download tracking
- Persisted to local database/storage
- The `file_path` serves as the physical link to the actual downloaded content

---

### 3. UserPreferences (Singleton Entity)

Stores user preferences and configuration. This is a **singleton entity** - only one instance exists per user.

**Attributes:**
- `id`: UUID - Unique identifier (always the same UUID for singleton - e.g., a well-known UUID)
- `default_download_path`: FilePath - Default path to save downloads
- `favorite_paths`: list[FilePath] - User's favorite download locations (for quick selection)
- `favorite_aggregators`: list[AggregatorSource] - Preferred torrent sources
- `max_concurrent_downloads`: int - Maximum simultaneous downloads (default: 3)
- `auto_start_downloads`: bool - Auto-start downloads on add (default: True)
- `date_created`: datetime - When preferences were first created
- `date_modified`: datetime - Last modification time

**Business Rules:**
- Only one UserPreferences instance exists (singleton pattern)
- `default_download_path` must always be set and valid
- `favorite_paths` can be empty list (no favorites yet)
- `favorite_aggregators` can be empty list (means use all available)
- `max_concurrent_downloads` must be >= 1 and <= 10
- `auto_start_downloads` defaults to True
- Modifications always update `date_modified`
- Cannot delete UserPreferences, only modify

**Domain Methods:**
```python
def add_favorite_path(self, path: FilePath) -> None:
    """Add path to favorites if not already present"""
    if path not in self.favorite_paths:
        self.favorite_paths.append(path)
        self.date_modified = datetime.now()

def remove_favorite_path(self, path: FilePath) -> None:
    """Remove path from favorites"""
    if path in self.favorite_paths:
        self.favorite_paths.remove(path)
        self.date_modified = datetime.now()

def add_favorite_aggregator(self, source: AggregatorSource) -> None:
    """Add aggregator to favorites if not already present"""
    if source not in self.favorite_aggregators:
        self.favorite_aggregators.append(source)
        self.date_modified = datetime.now()

def remove_favorite_aggregator(self, source: AggregatorSource) -> None:
    """Remove aggregator from favorites"""
    if source in self.favorite_aggregators:
        self.favorite_aggregators.remove(source)
        self.date_modified = datetime.now()

def update_default_path(self, path: FilePath) -> None:
    """Change default download path"""
    self.default_download_path = path
    self.date_modified = datetime.now()

def update_max_concurrent_downloads(self, max_count: int) -> None:
    """Update max concurrent downloads with validation"""
    if not (1 <= max_count <= 10):
        raise ValidationError("max_concurrent_downloads must be between 1 and 10")
    self.max_concurrent_downloads = max_count
    self.date_modified = datetime.now()

def update_auto_start(self, enabled: bool) -> None:
    """Toggle auto-start downloads"""
    self.auto_start_downloads = enabled
    self.date_modified = datetime.now()
```

**Factory Method:**
```python
@classmethod
def create_default(cls) -> "UserPreferences":
    """Create UserPreferences with default values"""
    return cls(
        id=UUID("00000000-0000-0000-0000-000000000001"),  # Well-known singleton ID
        default_download_path=FilePath(Path.home() / "Downloads"),
        favorite_paths=[],
        favorite_aggregators=[],
        max_concurrent_downloads=3,
        auto_start_downloads=True,
        date_created=datetime.now(),
        date_modified=datetime.now()
    )
```

**Notes:**
- Singleton pattern ensures only one preferences instance
- Persisted to database with well-known UUID
- All download-related preferences stored here (not in infrastructure config)
- Infrastructure config (qBittorrent, DB connection) stays separate
- Can be extended with new preferences without breaking existing code

---

### 4. DownloadHistory (Optional - Future Enhancement)
Simple audit log of download events. Can be added later if needed.

**Attributes:**
- `id`: UUID - Unique identifier
- `download_id`: UUID - Foreign key reference to Download
- `event_type`: enum - Type of event
  - `STARTED`
  - `COMPLETED`
  - `FAILED`
  - `REMOVED`
- `timestamp`: datetime - When the event occurred
- `notes`: string (nullable) - Additional context or error messages

**Notes:**
- Optional for MVP
- Useful for debugging and tracking download lifecycle
- Can be implemented later without affecting core functionality

---

## Entity Relationships

```
TorrentSearchResult (ephemeral)
    |
    | (user selects result)
    |
    v
Download (persisted)
    |
    | (optional tracking)
    |
    v
DownloadHistory (persisted)
```

---

## Value Objects

Value objects are immutable objects that represent descriptive aspects of the domain with no conceptual identity. They are defined by their attributes rather than a unique ID.

### 1. MagnetLink

Represents a magnet URI for BitTorrent downloads.

**Attributes:**
- `uri`: string - The full magnet link (e.g., "magnet:?xt=urn:btih:...")

**Validation Rules:**
- Must start with "magnet:?"
- Must contain "xt=urn:btih:" (the info hash)
- Info hash must be 40 characters (SHA-1) or 64 characters (SHA-256)
- Should be immutable once created

**Methods:**
- `from_string(uri: str) -> MagnetLink` - Factory method with validation
- `get_info_hash() -> str` - Extracts the torrent info hash
- `__str__() -> str` - Returns the full magnet URI
- `__eq__(other) -> bool` - Two magnet links are equal if their info hashes match

**Example:**
```python
magnet = MagnetLink.from_string("magnet:?xt=urn:btih:abc123...")
info_hash = magnet.get_info_hash()  # "abc123..."
```

**Notes:**
- Magnet links can contain additional parameters (trackers, display name, etc.)
- For equality, only the info hash matters (same torrent = same content)
- Invalid magnet links should raise a ValueError during creation

---

### 2. FileSize

Represents the size of a file with human-readable formatting.

**Attributes:**
- `bytes`: int - Size in bytes (canonical representation)

**Validation Rules:**
- Must be non-negative
- Immutable once created

**Methods:**
- `from_bytes(size: int) -> FileSize` - Create from byte count
- `from_string(size: str) -> FileSize` - Parse from human-readable string (e.g., "1.5 GB", "750 MB")
- `to_human_readable() -> str` - Convert to human-readable format with appropriate unit
- `__str__() -> str` - Returns human-readable format
- `__eq__(other) -> bool` - Compare based on byte value
- `__lt__(other) -> bool` - Enable size comparisons

**Supported Units:**
- B (bytes)
- KB (kilobytes)
- MB (megabytes)  
- GB (gigabytes)
- TB (terabytes)

**Example:**
```python
size1 = FileSize.from_bytes(1_500_000_000)
print(size1)  # "1.40 GB"

size2 = FileSize.from_string("750 MB")
print(size2.bytes)  # 786432000

if size1 > size2:
    print("size1 is larger")
```

**Notes:**
- Store internally as bytes for precision
- Use 1024-based conversion (1 KB = 1024 bytes) - binary units
- Handle parsing of various formats: "1.5GB", "1.5 GB", "1500MB", etc.
- Round to 2 decimal places for display

---

### 3. FilePath

Represents a file system path. Uses Python's built-in `pathlib.Path` object.

**Wrapper/Alias:**
```python
from pathlib import Path
FilePath = Path  # Type alias for clarity in domain model
```

**Why use pathlib.Path:**
- Built-in validation and normalization
- Cross-platform compatibility (Windows/Linux/Mac)
- Rich API for path manipulation
- Already immutable for practical purposes

**Common Operations:**
- `path.exists() -> bool` - Check if file/directory exists
- `path.is_file() -> bool` - Check if it's a file
- `path.is_dir() -> bool` - Check if it's a directory
- `path.parent -> Path` - Get parent directory
- `path.name -> str` - Get filename
- `path.resolve() -> Path` - Get absolute path

**Example:**
```python
download_path = FilePath("/home/user/downloads/movie.mkv")
if not download_path.parent.exists():
    download_path.parent.mkdir(parents=True)

print(download_path.name)  # "movie.mkv"
print(download_path.is_file())  # True/False
```

**Validation in Domain:**
- Verify parent directory exists or can be created
- Check write permissions
- Ensure path is absolute (or convert to absolute)
- Prevent path traversal attacks if accepting user input

**Notes:**
- Don't reinvent the wheel - `pathlib.Path` is excellent
- Wrap in custom class only if you need additional domain-specific validation
- Consider creating helper methods like `ensure_parent_exists()` if needed

---

### 4. AggregatorSource

Represents the source aggregator/indexer where a torrent was found.

**Attributes:**
- `name`: string - The aggregator name (e.g., "1337x", "ThePirateBay", "RARBG")

**Validation Rules:**
- Must be non-empty
- Should be from a known list of supported aggregators
- Case-insensitive but stored in canonical format
- Immutable once created

**Methods:**
- `from_string(name: str) -> AggregatorSource` - Factory method with validation
- `__str__() -> str` - Returns the canonical name
- `__eq__(other) -> bool` - Case-insensitive equality

**Supported Aggregators (Examples):**
- `1337x`
- `ThePirateBay` 
- `RARBG`
- `Nyaa` (for anime)
- `TorrentGalaxy`
- `LimeTorrents`

**Example:**
```python
source1 = AggregatorSource.from_string("1337x")
source2 = AggregatorSource.from_string("1337X")  # Case insensitive
print(source1 == source2)  # True

print(source1)  # "1337x" (canonical format)
```

**Notes:**
- Maintain a registry of supported aggregators
- Can add metadata like base URLs, reliability score, etc. later
- Helps ensure consistency in source naming across the application
- Makes it easy to filter/group downloads by source

---

## Design Principles

1. **Separation of Concerns**: Search results are separate from actual downloads
2. **Single Responsibility**: Each entity has one clear purpose
3. **Minimal Viable Design**: Start with just Download entity, add SearchResult for UX, add History later if needed
4. **Local First**: No cloud sync, no user auth - everything local
5. **File as Identity**: The downloaded file itself is the source of truth

---

## Data Transfer Objects (DTOs)

DTOs are used to transfer data between layers. They should be implemented as immutable dataclasses and organized as **inner classes within their corresponding use cases**.

### DTO Requirements

All input and output data objects must be implemented as **frozen dataclasses** with the following decorators:

```python
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True, slots=True)
class ExampleDTO:
    field1: str
    field2: int
```

**Decorator Explanation:**
- `frozen=True` - Makes the dataclass immutable (cannot modify after creation)
- `kw_only=True` - Requires keyword arguments (prevents positional argument errors)
- `slots=True` - Optimizes memory usage and prevents dynamic attribute assignment

### DTO Organization

DTOs should be defined as **inner classes** within their use case classes, named `InputData` and `OutputData`:

```python
class SearchTorrentsUseCase:
    """Use case for searching torrents across aggregators"""
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        query: str
        aggregator_names: list[str] | None = None
        max_results: int = 10
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        results: list['TorrentSearchResultDTO']
    
    def execute(self, input_data: InputData) -> OutputData:
        # Use case logic here
        pass
```

**Benefits of Inner Classes:**
- **Encapsulation** - DTOs are tightly coupled to their use case
- **Discoverability** - Easy to find which DTOs belong to which use case
- **Namespacing** - Avoids naming conflicts (multiple use cases can have `InputData`)
- **Cohesion** - Keeps related code together

### Shared DTOs

Some DTOs are used across multiple use cases and should be defined separately:

```python
@dataclass(frozen=True, kw_only=True, slots=True)
class DownloadDTO:
    """Shared DTO for representing a download across multiple use cases"""
    id: str  # UUID as string
    magnet_link: str
    title: str
    file_path: str
    source: str
    status: str
    date_added: datetime
    date_completed: datetime | None
    size: str

@dataclass(frozen=True, kw_only=True, slots=True)
class TorrentSearchResultDTO:
    """Shared DTO for representing search results"""
    magnet_link: str
    title: str
    size: str
    seeders: int
    leechers: int
    source: str
    date_found: datetime
```

### Usage Example

```python
# Creating input
input_data = SearchTorrentsUseCase.InputData(
    query="ubuntu",
    max_results=20
)

# Executing use case
use_case = SearchTorrentsUseCase(aggregator_service=...)
output_data = use_case.execute(input_data)

# Accessing results
for result in output_data.results:
    print(result.title)
```

**Notes:**
- Use type hints for all fields
- Use `| None` for optional fields (Python 3.10+)
- Provide default values where appropriate
- Keep DTOs simple - no business logic
- DTOs live in the application layer, separate from domain entities
- Use descriptive names like `InputData` and `OutputData` for consistency

---

## Use Case Error Handling

All use cases should raise domain-specific exceptions when errors occur. These exceptions should be caught and handled by the external layer (CLI, API, etc.).

### Standard Exceptions

**Domain Exceptions:**
```python
class DomainException(Exception):
    """Base exception for all domain errors"""
    pass

class ValidationError(DomainException):
    """Raised when input validation fails"""
    pass

class DownloadNotFoundError(DomainException):
    """Raised when a download cannot be found"""
    pass

class DuplicateDownloadError(DomainException):
    """Raised when attempting to add a duplicate download"""
    pass

class InvalidStateTransitionError(DomainException):
    """Raised when attempting an invalid status change"""
    pass

class TorrentClientError(DomainException):
    """Raised when torrent client operations fail"""
    pass

class AggregatorError(DomainException):
    """Raised when aggregator search fails"""
    pass

class AggregatorTimeoutError(AggregatorError):
    """Raised when aggregator search times out"""
    pass

class FileSystemError(DomainException):
    """Raised when file system operations fail"""
    pass
```

### Error Handling Guidelines

1. **Always raise exceptions** - Don't return error codes or null values
2. **Be specific** - Use the most specific exception type
3. **Include context** - Pass helpful error messages
4. **Let it bubble** - Don't catch exceptions in use cases unless you can handle them
5. **Document exceptions** - List possible exceptions in use case documentation

**Example:**
```python
def add_download(self, input_data: AddDownloadInput) -> DownloadDTO:
    # Validate and create value objects
    try:
        magnet = MagnetLink.from_string(input_data.magnet_link)
    except ValueError as e:
        raise ValidationError(f"Invalid magnet link: {e}")
    
    # Check for duplicates
    if self.repository.exists(magnet):
        raise DuplicateDownloadError(f"Download already exists: {magnet}")
    
    # ... rest of use case
```

**External Layer Handling:**
```python
# In CLI layer
try:
    result = use_case.add_download(input_dto)
    print(f"Download added: {result.title}")
except ValidationError as e:
    print(f"Error: {e}")
    sys.exit(1)
except DuplicateDownloadError as e:
    print(f"Error: {e}")
    sys.exit(1)
```

---

## Use Cases

Use cases represent the application's business logic and orchestrate the flow between entities, repositories, and external services.

### Summary

The application has **13 use cases** organized into two categories:

**Download Management (7 use cases):**
1. SearchTorrents - Search for torrents across aggregators
2. AddDownload - Add and start a download
3. ListDownloads - List all downloads with filtering
4. GetDownloadStatus - Get current status and progress
5. RemoveDownload - Remove a download
6. PauseDownload - Pause an active download  
7. ResumeDownload - Resume a paused download
8. RefreshDownloads - Sync status with torrent client

**User Preferences Management (5 use cases):**
9. GetUserPreferences - Load preferences at startup
10. UpdateUserPreferences - Update preference settings
11. AddFavoritePath - Add favorite download location
12. RemoveFavoritePath - Remove favorite location
13. AddFavoriteAggregator - Add favorite torrent source
14. RemoveFavoriteAggregator - Remove favorite source

Total: **14 use cases**

---

### 1. SearchTorrents

Search for torrents across multiple aggregators based on a query.

**Use Case Structure:**
```python
class SearchTorrentsUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        query: str
        aggregator_names: list[str] | None = None
        max_results: int = 10
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        results: list[TorrentSearchResultDTO]
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Validate query is not empty (raise ValidationError if empty)
2. Determine which aggregators to use:
   - If aggregator_names provided in input, use those
   - Otherwise, load UserPreferences via preferences_repository.get()
   - If preferences.favorite_aggregators is not empty, use those
   - If empty, use all available aggregators
3. Convert aggregator_names to AggregatorSource value objects
4. For each aggregator source:
   - Get corresponding IAggregatorService implementation
   - Call service.search() which returns TorrentSearchResult entities
   - Handle failures gracefully (skip failed sources)
5. Combine all TorrentSearchResult entities
6. Deduplicate by magnet link (keep first occurrence)
7. Sort by seeders (descending)
8. Convert entities to TorrentSearchResultDTO objects
9. Return OutputData with list of DTOs

**Exceptions Raised:**
- `ValidationError` - When query is empty or invalid
- `AggregatorError` - When all aggregators fail (at least one must succeed)
- `AggregatorTimeoutError` - When aggregator search times out

**Business Rules:**
- Empty queries should be rejected
- Uses favorite_aggregators from preferences if no aggregators specified
- Empty favorites list means "use all available aggregators"
- Results should be deduplicated by magnet link (same torrent from different sources)
- Should handle aggregator failures gracefully (skip failed sources, don't crash)
- Should timeout after reasonable duration per aggregator (e.g., 10 seconds)
- At least one aggregator must succeed, otherwise raise AggregatorError

**Interfaces Needed:**
- `IAggregatorService` - For searching external aggregators
- `IUserPreferencesRepository` - For loading favorite aggregators

---

### 2. AddDownload

Add a torrent to downloads and start downloading it.

**Use Case Structure:**
```python
class AddDownloadUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        magnet_link: str
        title: str
        source: str
        size: str
        download_directory: str | None = None
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        download: DownloadDTO
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Create MagnetLink value object from input (raises ValidationError if invalid)
2. Create AggregatorSource value object from source string
3. Create FileSize value object from size string
4. Check if download already exists via repository.find_by_magnet_link()
   - If exists: raise DuplicateDownloadError
5. Determine download directory:
   - If download_directory provided in input, use it
   - Otherwise, load UserPreferences via preferences_repository.get()
   - Use preferences.default_download_path
6. Sanitize title for file path (remove special characters)
7. Create FilePath value object (download_directory + sanitized title)
8. Verify parent directory exists/is creatable (raise FileSystemError if not)
9. Create new Download entity with:
   - Generated UUID
   - MagnetLink, title, AggregatorSource, FileSize, FilePath
   - Status = DOWNLOADING
   - Current datetime for date_added
10. Save via repository.save()
11. Start download via torrent_client.add_torrent() (raises TorrentClientError if fails)
12. Convert Download entity to DownloadDTO
13. Return OutputData with DTO

**Exceptions Raised:**
- `ValidationError` - Invalid magnet link, size format, or source name
- `DuplicateDownloadError` - Download with same magnet link already exists
- `FileSystemError` - Cannot create download directory or no write permissions
- `TorrentClientError` - Failed to start download in torrent client

**Business Rules:**
- Cannot add duplicate downloads (same magnet link)
- Uses user's default_download_path from preferences if no directory specified
- Download directory must exist or be creatable
- Must have write permissions to download directory
- Sanitize title for use in file path (remove special characters)
- Invalid magnet links should raise validation error

**Interfaces Needed:**
- `IDownloadRepository` - For persisting downloads
- `IUserPreferencesRepository` - For loading default download path
- `ITorrentClient` - For starting the actual download

---

### 3. ListDownloads

Retrieve all downloads, optionally filtered by status.

**Use Case Structure:**
```python
class ListDownloadsUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        status: str | None = None
        sort_by: str = "date_added"
        ascending: bool = False
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        downloads: list[DownloadDTO]
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. If status provided, convert to DownloadStatus enum (raises ValidationError if invalid)
2. Validate sort_by field exists on Download entity (raises ValidationError if invalid)
3. Query repository.find_all() with filters
4. Sort Download entities according to criteria
5. Convert each Download entity to DownloadDTO
6. Return OutputData with list of DTOs

**Exceptions Raised:**
- `ValidationError` - Invalid status value or sort_by field

**Business Rules:**
- Default sort should be by date_added (newest first)
- Should handle empty results gracefully (return empty list)
- Invalid status values should raise validation error
- Valid statuses: "DOWNLOADING", "COMPLETED", "FAILED", "PAUSED"

**Interfaces Needed:**
- `IDownloadRepository` - For querying downloads

---

### 4. GetDownloadStatus

Get the current status and progress of a specific download.

**Use Case Structure:**
```python
class GetDownloadStatusUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        download_id: str  # UUID as string
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        download: DownloadDTO
        progress: float  # 0.0 to 100.0
        download_rate: str  # e.g., "1.5 MB/s"
        upload_rate: str
        eta: str  # e.g., "5 minutes"
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Convert download_id string to UUID (raises ValidationError if invalid)
2. Retrieve Download entity via repository.find_by_id()
3. If not found, raise DownloadNotFoundError
4. Query torrent_client.get_torrent_status() with download's torrent_id
   - If client error, raise TorrentClientError
5. If status changed (e.g., progress reached 100%):
   - Update Download entity status to COMPLETED
   - Set date_completed if newly completed
   - Save via repository.save()
6. Convert Download entity to DownloadDTO
7. Format progress info (convert bytes/sec to human readable)
8. Create and return OutputData with download and progress fields

**Exceptions Raised:**
- `ValidationError` - Invalid UUID format
- `DownloadNotFoundError` - Download with given ID not found
- `TorrentClientError` - Failed to get status from torrent client

**Business Rules:**
- If download not found, raise DownloadNotFoundError
- If torrent client has no info, download may have been removed from client
- Update status to COMPLETED when progress reaches 100%
- Speed rates should be human-readable (e.g., "1.5 MB/s" not bytes)

**Interfaces Needed:**
- `IDownloadRepository` - For retrieving/updating downloads
- `ITorrentClient` - For getting progress information

---

### 5. RemoveDownload

Remove a download from tracking (optionally delete files).

**Use Case Structure:**
```python
class RemoveDownloadUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        download_id: str  # UUID as string
        delete_files: bool = False
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        success: bool
        download_id: str
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Convert download_id string to UUID (raises ValidationError if invalid)
2. Retrieve Download entity via repository.find_by_id()
3. If not found, raise DownloadNotFoundError
4. Stop download in torrent_client.remove_torrent() (pass delete_files flag)
   - If client error but download exists in DB, continue (client might not have it)
5. If delete_files is True and files exist:
   - Delete files from file system using FilePath from entity
   - If deletion fails, raise FileSystemError
6. Delete download record via repository.delete()
7. Create OutputData with success=True and download_id
8. Return OutputData

**Exceptions Raised:**
- `ValidationError` - Invalid UUID format
- `DownloadNotFoundError` - Download with given ID not found
- `FileSystemError` - Failed to delete files from disk
- `TorrentClientError` - Failed to remove from client (non-fatal, continues to DB deletion)

**Business Rules:**
- Cannot remove non-existent downloads
- Assumes deletion confirmation has been handled in outer layer (UI/CLI)
- Should handle case where files already deleted manually (don't fail)
- Should handle case where download not in torrent client (still remove from DB)

**Interfaces Needed:**
- `IDownloadRepository` - For deleting downloads
- `ITorrentClient` - For stopping/removing from client
- `IFileSystem` (optional) - For file deletion

---

### 6. PauseDownload / ResumeDownload

Pause or resume an active download.

**Use Case Structure:**
```python
class PauseDownloadUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        download_id: str  # UUID as string
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        download: DownloadDTO
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass

class ResumeDownloadUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        download_id: str  # UUID as string
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        download: DownloadDTO
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow (Pause):**
1. Convert download_id string to UUID (raises ValidationError if invalid)
2. Retrieve Download entity via repository.find_by_id()
3. If not found, raise DownloadNotFoundError
4. Verify status is DOWNLOADING (raise InvalidStateTransitionError if not)
5. Pause in torrent_client.pause_torrent()
   - If fails, raise TorrentClientError
6. Update Download entity status to PAUSED
7. Save via repository.save()
8. Convert Download entity to DownloadDTO
9. Return OutputData with DTO

**Flow (Resume):**
1. Convert download_id string to UUID (raises ValidationError if invalid)
2. Retrieve Download entity via repository.find_by_id()
3. If not found, raise DownloadNotFoundError
4. Verify status is PAUSED (raise InvalidStateTransitionError if not)
5. Resume in torrent_client.resume_torrent()
   - If fails, raise TorrentClientError
6. Update Download entity status to DOWNLOADING
7. Save via repository.save()
8. Convert Download entity to DownloadDTO
9. Return OutputData with DTO

**Exceptions Raised:**
- `ValidationError` - Invalid UUID format
- `DownloadNotFoundError` - Download with given ID not found
- `InvalidStateTransitionError` - Cannot pause/resume from current status
- `TorrentClientError` - Failed to pause/resume in torrent client

**Business Rules:**
- Can only pause DOWNLOADING torrents
- Can only resume PAUSED torrents
- If client no longer has torrent, raise TorrentClientError
- Invalid state transitions should raise InvalidStateTransitionError

**Interfaces Needed:**
- `IDownloadRepository` - For updating downloads
- `ITorrentClient` - For pause/resume operations

---

### 7. RefreshDownloads

Sync download statuses with torrent client. Can be called manually or by external scheduler.

**Use Case Structure:**
```python
class RefreshDownloadsUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        pass  # No input required
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        updated_count: int
        failed_count: int
        error_messages: list[str]
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Get all active downloads via repository.find_all() with status filter (DOWNLOADING, PAUSED)
2. Initialize counters: updated_count=0, failed_count=0, errors=[]
3. For each Download entity:
   - Try to query torrent_client.get_torrent_status() with torrent_id
   - If client error, add to error_messages, increment failed_count, continue
   - Compare client status with entity status
   - If different, update Download entity:
     - Update status field
     - If completed (progress = 100%), set date_completed and status=COMPLETED
     - If missing from client or error, set status to FAILED
   - Save updated entity via repository.save()
   - Increment updated_count if changes were made
4. Create OutputData with counts and errors
5. Return OutputData

**Exceptions Raised:**
- Generally catches and records errors rather than raising them
- Only raises if critical repository errors occur

**Business Rules:**
- Should handle client disconnection gracefully (record error, continue)
- Should not interfere with user operations
- Only updates downloads with active statuses (DOWNLOADING, PAUSED)
- Scheduling/timing is handled by external layer (not use case responsibility)
- Records partial failures rather than failing entirely

**Interfaces Needed:**
- `IDownloadRepository` - For batch updates
- `ITorrentClient` - For status queries

---

### 8. GetUserPreferences

Load user preferences at application startup or when needed.

**Use Case Structure:**
```python
class GetUserPreferencesUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        pass  # No input required
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        preferences: UserPreferencesDTO
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Call repository.get() to retrieve UserPreferences singleton
   - If doesn't exist, repository auto-creates with defaults
2. Convert UserPreferences entity to UserPreferencesDTO
3. Return OutputData with DTO

**Exceptions Raised:**
- Generally doesn't raise exceptions (repository handles creation)
- May raise if database is completely unavailable

**Business Rules:**
- Always returns preferences (creates defaults if none exist)
- Should be called once at application startup
- Result can be cached in memory for application lifetime

**Interfaces Needed:**
- `IUserPreferencesRepository` - For loading preferences

**DTO:**
```python
@dataclass(frozen=True, kw_only=True, slots=True)
class UserPreferencesDTO:
    id: str
    default_download_path: str
    favorite_paths: list[str]
    favorite_aggregators: list[str]
    max_concurrent_downloads: int
    auto_start_downloads: bool
    date_created: datetime
    date_modified: datetime
```

---

### 9. UpdateUserPreferences

Update one or more user preference settings.

**Use Case Structure:**
```python
class UpdateUserPreferencesUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        default_download_path: str | None = None
        max_concurrent_downloads: int | None = None
        auto_start_downloads: bool | None = None
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        preferences: UserPreferencesDTO
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Load existing UserPreferences via repository.get()
2. For each non-None field in InputData:
   - Validate the value
   - Call corresponding entity update method:
     - `default_download_path` → `update_default_path(FilePath)`
     - `max_concurrent_downloads` → `update_max_concurrent_downloads(int)`
     - `auto_start_downloads` → `update_auto_start(bool)`
3. Save updated entity via repository.save()
4. Convert entity to DTO
5. Return OutputData with updated preferences

**Exceptions Raised:**
- `ValidationError` - Invalid path format or invalid max_concurrent_downloads range
- `FileSystemError` - If default_download_path doesn't exist or can't be created

**Business Rules:**
- Only updates fields that are provided (partial updates)
- Validates all inputs before making any changes
- Updates date_modified automatically
- At least one field must be provided

**Interfaces Needed:**
- `IUserPreferencesRepository` - For loading and saving

---

### 10. AddFavoritePath

Add a path to user's favorite download locations.

**Use Case Structure:**
```python
class AddFavoritePathUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        path: str
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        preferences: UserPreferencesDTO
        was_added: bool  # False if already existed
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Validate path string and convert to FilePath value object
2. Load UserPreferences via repository.get()
3. Check if path already in favorites
4. If not, call preferences.add_favorite_path(path)
5. Save updated entity via repository.save()
6. Convert to DTO and return with was_added flag

**Exceptions Raised:**
- `ValidationError` - Invalid path format
- `FileSystemError` - Path doesn't exist or can't be accessed

**Business Rules:**
- Path must exist or be creatable
- Duplicate paths are silently ignored (idempotent)
- No limit on number of favorite paths

**Interfaces Needed:**
- `IUserPreferencesRepository`

---

### 11. RemoveFavoritePath

Remove a path from user's favorite download locations.

**Use Case Structure:**
```python
class RemoveFavoritePathUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        path: str
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        preferences: UserPreferencesDTO
        was_removed: bool  # False if didn't exist
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Convert path string to FilePath value object
2. Load UserPreferences via repository.get()
3. Check if path in favorites
4. If yes, call preferences.remove_favorite_path(path)
5. Save updated entity via repository.save()
6. Convert to DTO and return with was_removed flag

**Exceptions Raised:**
- `ValidationError` - Invalid path format

**Business Rules:**
- Removing non-existent path is not an error (idempotent)
- Cannot remove default_download_path from favorites (separate field)

**Interfaces Needed:**
- `IUserPreferencesRepository`

---

### 12. AddFavoriteAggregator

Add an aggregator to user's favorites.

**Use Case Structure:**
```python
class AddFavoriteAggregatorUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        aggregator_name: str
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        preferences: UserPreferencesDTO
        was_added: bool
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Validate aggregator name and convert to AggregatorSource value object
2. Load UserPreferences via repository.get()
3. Check if aggregator already in favorites
4. If not, call preferences.add_favorite_aggregator(source)
5. Save via repository.save()
6. Return DTO with was_added flag

**Exceptions Raised:**
- `ValidationError` - Unknown aggregator name

**Business Rules:**
- Only valid aggregator names accepted
- Duplicates ignored (idempotent)
- Empty favorites list means "use all aggregators"

**Interfaces Needed:**
- `IUserPreferencesRepository`

---

### 13. RemoveFavoriteAggregator

Remove an aggregator from user's favorites.

**Use Case Structure:**
```python
class RemoveFavoriteAggregatorUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        aggregator_name: str
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        preferences: UserPreferencesDTO
        was_removed: bool
    
    def execute(self, input_data: InputData) -> OutputData:
        # Implementation here
        pass
```

**Flow:**
1. Convert aggregator name to AggregatorSource value object
2. Load UserPreferences via repository.get()
3. Check if aggregator in favorites
4. If yes, call preferences.remove_favorite_aggregator(source)
5. Save via repository.save()
6. Return DTO with was_removed flag

**Exceptions Raised:**
- `ValidationError` - Unknown aggregator name

**Business Rules:**
- Removing non-existent aggregator is not an error (idempotent)
- If all aggregators removed, defaults to using all available

**Interfaces Needed:**
- `IUserPreferencesRepository`

---

## Repository Interfaces

Repositories abstract data persistence and retrieval.

### IDownloadRepository

Handles persistence of Download entities.

**Methods:**

```python
def save(download: Download) -> Download:
    """Create or update a download"""
    pass

def find_by_id(download_id: UUID) -> Optional[Download]:
    """Find download by ID"""
    pass

def find_by_magnet_link(magnet_link: MagnetLink) -> Optional[Download]:
    """Find download by magnet link (check for duplicates)"""
    pass

def find_all(
    status: Optional[DownloadStatus] = None,
    sort_by: str = "date_added",
    ascending: bool = False
) -> list[Download]:
    """Find all downloads with optional filtering and sorting"""
    pass

def delete(download_id: UUID) -> bool:
    """Delete a download, returns True if successful"""
    pass

def update_status(download_id: UUID, status: DownloadStatus) -> Download:
    """Update download status"""
    pass

def exists(magnet_link: MagnetLink) -> bool:
    """Check if download already exists"""
    pass
```

**Notes:**
- Implementation could use SQLite, JSON files, or any data store
- Should handle concurrent access safely
- Should validate entities before saving

---

### IUserPreferencesRepository

Handles persistence of UserPreferences singleton entity.

**Methods:**

```python
def get() -> UserPreferences:
    """
    Get the singleton UserPreferences instance.
    If it doesn't exist, creates and returns default preferences.
    """
    pass

def save(preferences: UserPreferences) -> UserPreferences:
    """Save/update user preferences"""
    pass

def exists() -> bool:
    """Check if preferences exist in storage"""
    pass
```

**Notes:**
- This is a singleton repository - only one UserPreferences instance exists
- `get()` should automatically create default preferences if none exist
- Should use well-known UUID: `00000000-0000-0000-0000-000000000001`
- Implementation could use same database as downloads
- Thread-safe access important for concurrent operations

---

## External Service Interfaces

These interfaces define contracts for external dependencies.

### IAggregatorService

Interface for torrent search aggregators.

**Methods:**

```python
def search(
    query: str,
    max_results: int = 10,
    timeout: int = 10
) -> list[TorrentSearchResult]:
    """
    Search for torrents matching the query.
    
    Args:
        query: Search terms
        max_results: Maximum number of results to return
        timeout: Maximum time to wait for results (seconds)
    
    Returns:
        List of search results
        
    Raises:
        AggregatorTimeoutError: If search times out
        AggregatorError: If search fails
    """
    pass

def get_source() -> AggregatorSource:
    """Get the aggregator source this service represents"""
    pass

def is_available() -> bool:
    """Check if aggregator is currently reachable"""
    pass
```

**Implementation Notes:**
- Each aggregator (1337x, TPB, etc.) should have its own implementation
- Should handle site-specific parsing and scraping
- Should respect rate limits
- Should handle site changes gracefully

**Example Implementations:**
- `Aggregator1337xService`
- `AggregatorThePirateBayService`
- `AggregatorRARBGService`

---

### ITorrentClient

Interface for interacting with a BitTorrent client.

**Methods:**

```python
def add_torrent(
    magnet_link: MagnetLink,
    download_path: FilePath
) -> str:
    """
    Add a torrent to the client.
    
    Args:
        magnet_link: The magnet link to download
        download_path: Where to save the files
    
    Returns:
        torrent_id: Client-specific torrent identifier
        
    Raises:
        TorrentClientError: If adding torrent fails
    """
    pass

def get_torrent_status(torrent_id: str) -> dict:
    """
    Get current status of a torrent.
    
    Returns dict with:
        - status: str (downloading, seeding, paused, error)
        - progress: float (0.0 to 100.0)
        - download_rate: int (bytes per second)
        - upload_rate: int (bytes per second)
        - eta: int (seconds remaining, -1 if unknown)
    """
    pass

def pause_torrent(torrent_id: str) -> bool:
    """Pause a torrent"""
    pass

def resume_torrent(torrent_id: str) -> bool:
    """Resume a paused torrent"""
    pass

def remove_torrent(torrent_id: str, delete_files: bool = False) -> bool:
    """Remove torrent from client, optionally delete files"""
    pass

def get_all_torrents() -> list[str]:
    """Get list of all torrent IDs in client"""
    pass

def is_connected() -> bool:
    """Check if client is running and accessible"""
    pass
```

**Implementation Options:**
- `TransmissionClient` - For Transmission daemon
- `QBittorrentClient` - For qBittorrent
- `LibtorrentClient` - Direct libtorrent-rasterbar integration

**Notes:**
- Should handle client disconnection gracefully
- Should map client-specific states to our DownloadStatus enum
- Should store torrent_id in Download entity for tracking

---

### IFileSystem (Optional)

Interface for file system operations. Can use Python's built-in functions or wrap them.

**Methods:**

```python
def delete_file(path: FilePath) -> bool:
    """Delete a file"""
    pass

def delete_directory(path: FilePath) -> bool:
    """Delete a directory and its contents"""
    pass

def ensure_directory_exists(path: FilePath) -> bool:
    """Create directory if it doesn't exist"""
    pass

def get_file_size(path: FilePath) -> FileSize:
    """Get size of a file"""
    pass

def file_exists(path: FilePath) -> bool:
    """Check if file exists"""
    pass
```

**Notes:**
- Mostly a wrapper around pathlib operations
- Useful for testing (can mock file operations)
- Can add retry logic, permission handling, etc.

---

## Use Case Dependencies Summary

| Use Case | Repository | External Service |
|----------|-----------|------------------|
| SearchTorrents | - | IAggregatorService |
| AddDownload | IDownloadRepository | ITorrentClient |
| ListDownloads | IDownloadRepository | - |
| GetDownloadStatus | IDownloadRepository | ITorrentClient |
| RemoveDownload | IDownloadRepository | ITorrentClient, IFileSystem |
| PauseDownload | IDownloadRepository | ITorrentClient |
| ResumeDownload | IDownloadRepository | ITorrentClient |
| RefreshDownloads | IDownloadRepository | ITorrentClient |

---

## Next Steps for Implementation

1. ~~Define value objects~~ ✓
2. ~~Define repository interfaces~~ ✓
3. ~~Define use cases/application services~~ ✓
4. ~~Define external service interfaces~~ ✓
5. Implement infrastructure layer (database, external APIs)
6. Build CLI interface

---

## Technology Stack

### Core Technologies

- **Language**: Python 3.11+
- **Package Manager**: UV (fast, modern Python package manager)
- **Database**: SQLite (file-based, easily transferable)
- **ORM**: SQLAlchemy 2.0+
- **Torrent Client**: qBittorrent with `qbittorrent-api` Python client
- **Torrent Search**: `torrent-search-python` library
- **CLI Framework**: Typer
- **Terminal UI**: Rich (for beautiful output, tables, progress bars)

### Dependencies

```toml
[project]
name = "torrent-cli"
version = "0.1.0"
description = "CLI torrent download manager"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12.0",
    "rich>=13.7.0",
    "sqlalchemy>=2.0",
    "qbittorrent-api>=2024.1",
    "torrent-search-python>=1.0",
    "requests>=2.31.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
    "mkdocstrings[python]>=0.24.0",
]
```

### Installation with UV

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
uv init torrent-cli
cd torrent-cli

# Add dependencies
uv add typer rich sqlalchemy qbittorrent-api torrent-search-python requests pydantic

# Add dev dependencies
uv add --dev pytest pytest-cov mypy ruff mkdocs mkdocs-material mkdocstrings[python]

# Run the application
uv run python -m src.infrastructure.cli.main
```

### Quick Start Commands

```bash
# Format code
ruff format .

# Check linting
ruff check --fix .

# Run tests with coverage
pytest --cov=src --cov-fail-under=100

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Dependency Injection with Protocols

**All external dependencies must be injected through Protocols to enable:**
- Easy testing with mock objects
- Loose coupling between layers
- Ability to swap implementations without changing business logic
- **Interface adapters can be tested in isolation**

**The key principle: Inject all the way down - even interface adapters depend on abstractions**

#### Three Levels of Abstraction:

1. **Domain Interfaces** (for application layer) - ABC
2. **Interface Adapter Protocols** (for interface adapters layer internals) - Protocol
3. **Concrete External Libraries** (injected only at infrastructure/composition root)

**Example Pattern:**

```python
from typing import Protocol
from abc import ABC, abstractmethod

# ============================================
# LEVEL 1: Domain Interface (for Use Cases)
# ============================================
# Located in: src/domain/services/torrent_client.py

class ITorrentClient(ABC):
    """Domain interface - used by application layer"""
    @abstractmethod
    def add_torrent(self, magnet_link: MagnetLink, download_path: FilePath) -> str:
        pass
    
    @abstractmethod
    def get_torrent_status(self, torrent_id: str) -> dict:
        pass

# ============================================
# LEVEL 2: Interface Adapter Protocol (for Adapter Implementation)
# ============================================
# Located in: src/interface_adapters/protocols/qbittorrent_protocol.py

class QBittorrentClientProtocol(Protocol):
    """Protocol for the external qbittorrent-api Client object"""
    
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
    
    def torrents_delete(self, torrent_hashes: str, delete_files: bool = False) -> None:
        """Delete torrents"""
        ...
    
    def auth_log_in(self, username: str, password: str) -> None:
        """Authenticate with qBittorrent"""
        ...

# ============================================
# LEVEL 3: Interface Adapter Implementation
# ============================================
# Located in: src/interface_adapters/torrent_clients/qbittorrent_client.py

class QBittorrentClient(ITorrentClient):
    """Concrete implementation - receives external client via constructor"""
    
    def __init__(self, client: QBittorrentClientProtocol):
        """
        Inject the actual qbittorrent-api Client through protocol.
        This allows us to test with a mock that matches the protocol.
        """
        self.client = client
    
    def add_torrent(self, magnet_link: MagnetLink, download_path: FilePath) -> str:
        """Implement domain interface using injected client"""
        result = self.client.torrents_add(
            urls=str(magnet_link),
            save_path=str(download_path)
        )
        # Extract and return torrent hash/id
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

# ============================================
# Application Layer - Use Case with Domain Interface
# ============================================
# Located in: src/application/use_cases/add_download.py

class AddDownloadUseCase:
    def __init__(
        self,
        repository: IDownloadRepository,
        torrent_client: ITorrentClient  # Domain interface, not concrete class
    ):
        self.repository = repository
        self.torrent_client = torrent_client
    
    def execute(self, input_data: InputData) -> OutputData:
        # Use injected dependencies through domain interfaces
        pass

# ============================================
# Infrastructure Layer - Composition Root
# ============================================
# Located in: src/infrastructure/cli/main.py or src/infrastructure/di/container.py

import qbittorrentapi

def create_qbittorrent_client(config: Config) -> ITorrentClient:
    """Factory function to create configured qBittorrent client"""
    
    # Create the actual external library client
    qbt_client = qbittorrentapi.Client(
        host=config.qbt_host,
        port=config.qbt_port,
        username=config.qbt_username,
        password=config.qbt_password
    )
    qbt_client.auth_log_in()
    
    # Inject it into our interface adapter
    # The qbittorrentapi.Client object satisfies QBittorrentClientProtocol
    return QBittorrentClient(client=qbt_client)

def main():
    # Load configuration
    config = Config.load()
    
    # Create all interface adapter implementations
    repository = SQLiteDownloadRepository(
        engine=create_engine(f"sqlite:///{config.db_path}")
    )
    torrent_client = create_qbittorrent_client(config)
    aggregator = TorrentSearchAggregator(
        search_client=TorrentSearch()  # From torrent-search-python
    )
    
    # Inject into use case
    use_case = AddDownloadUseCase(
        repository=repository,
        torrent_client=torrent_client
    )
    
    # Execute
    result = use_case.execute(input_data)

# ============================================
# Testing - Interface Adapters Layer
# ============================================
# Located in: tests/unit/interface_adapters/test_qbittorrent_client.py

from unittest.mock import Mock
import pytest

def test_qbittorrent_client_add_torrent():
    """Test interface adapter implementation with mock protocol"""
    # Arrange - Create mock using autospec for type safety
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

def test_qbittorrent_client_get_status():
    """Test getting torrent status"""
    # Arrange
    mock_client = Mock(spec=QBittorrentClientProtocol)
    mock_client.torrents_info.return_value = [{
        'state': 'downloading',
        'progress': 0.45,
        'dlspeed': 1024 * 1024,  # 1 MB/s
        'upspeed': 512 * 1024,
        'eta': 3600
    }]
    
    qbt_client = QBittorrentClient(client=mock_client)
    
    # Act
    status = qbt_client.get_torrent_status("abc123")
    
    # Assert
    assert status['progress'] == 45.0
    assert status['status'] == 'downloading'
    mock_client.torrents_info.assert_called_once_with(torrent_hashes="abc123")

def test_qbittorrent_client_pause():
    """Test pausing a torrent"""
    # Arrange
    mock_client = Mock(spec=QBittorrentClientProtocol)
    qbt_client = QBittorrentClient(client=mock_client)
    
    # Act
    qbt_client.pause_torrent("abc123")
    
    # Assert
    mock_client.torrents_pause.assert_called_once_with(torrent_hashes="abc123")

# ============================================
# Testing - Application Layer
# ============================================
# Located in: tests/unit/application/test_add_download_use_case.py

from unittest.mock import Mock

def test_add_download_use_case():
    """Test use case with mock implementations"""
    # Arrange - Mock domain interfaces
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists.return_value = False
    mock_repo.save.return_value = Mock()  # Returns saved entity
    
    mock_client = Mock(spec=ITorrentClient)
    mock_client.add_torrent.return_value = "torrent_123"
    
    use_case = AddDownloadUseCase(
        repository=mock_repo,
        torrent_client=mock_client
    )
    
    input_data = AddDownloadUseCase.InputData(
        magnet_link="magnet:?xt=urn:btih:abc123...",
        title="Test Download",
        source="1337x",
        size="1.5 GB"
    )
    
    # Act
    result = use_case.execute(input_data)
    
    # Assert
    assert result.download.status == "DOWNLOADING"
    
    # Verify repository interactions
    mock_repo.exists.assert_called_once()
    mock_repo.save.assert_called_once()
    
    # Verify torrent client interactions
    mock_client.add_torrent.assert_called_once()
    call_args = mock_client.add_torrent.call_args
    assert isinstance(call_args[0][0], MagnetLink)  # First arg is MagnetLink
    assert isinstance(call_args[0][1], FilePath)    # Second arg is FilePath

def test_add_download_duplicate_error():
    """Test that duplicate downloads raise an error"""
    # Arrange
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists.return_value = True  # Download already exists
    
    mock_client = Mock(spec=ITorrentClient)
    
    use_case = AddDownloadUseCase(
        repository=mock_repo,
        torrent_client=mock_client
    )
    
    input_data = AddDownloadUseCase.InputData(
        magnet_link="magnet:?xt=urn:btih:abc123...",
        title="Test Download",
        source="1337x",
        size="1.5 GB"
    )
    
    # Act & Assert
    with pytest.raises(DuplicateDownloadError):
        use_case.execute(input_data)
    
    # Verify client was never called
    mock_client.add_torrent.assert_not_called()
```

### Testing Best Practices:

1. **Use `Mock(spec=Protocol)` or `Mock(spec=Interface)`**
   - Provides type safety and catches typos
   - Ensures you're only mocking methods that actually exist
   - Better IDE support

2. **Configure return values inline**
   ```python
   mock_client = Mock(spec=QBittorrentClientProtocol)
   mock_client.torrents_add.return_value = "torrent_hash"
   ```

3. **Verify method calls**
   ```python
   mock_client.torrents_add.assert_called_once_with(
       urls="magnet:?...",
       save_path="/downloads"
   )
   ```

4. **No need for custom mock classes**
   - Use `Mock(spec=)` instead
   - Configure behavior in test itself
   - More flexible and maintainable

5. **Test both success and error cases**
   - Happy path: Verify correct return values and method calls
   - Error path: Use `pytest.raises()` to test exceptions

### Key Principles:

1. **Protocol-Based Injection for Interface Adapters**
   - Interface adapter implementations receive external clients via constructor
   - Use `Protocol` to define the contract for external libraries
   - This allows testing interface adapters without the actual external library

2. **Three Layers of Abstraction**
   - **Domain Interface** (ABC) - Used by application layer
   - **Interface Adapter Protocol** (Protocol) - Contract for external libraries
   - **Concrete Implementation** - Bridges domain interface and external library

3. **Never import concrete implementations in domain/application layers**
   - Domain layer: Only entities, value objects, interfaces (ABC)
   - Application layer: Only use cases, DTOs, domain interfaces (ABC)
   - Interface Adapters layer: Protocols + concrete implementations
   - Infrastructure layer: Wires everything together (composition root)

4. **All dependencies injected via constructor at every level**
   ```python
   # Use Case receives domain interfaces
   def __init__(self, repository: IRepository, client: IClient):
       ...
   
   # Interface Adapter receives protocol-typed external dependencies
   def __init__(self, client: QBittorrentClientProtocol):
       ...
   ```

5. **Composition happens only in infrastructure layer**
   ```python
   # Create real external library objects
   qbt = qbittorrentapi.Client(...)
   
   # Inject into interface adapter
   client = QBittorrentClient(client=qbt)
   
   # Inject into use case
   use_case = AddDownloadUseCase(torrent_client=client)
   ```

6. **Testing at every level**
   - **Application layer tests**: Use `Mock(autospec=Interface)` for domain interfaces
   - **Interface Adapters layer tests**: Use `Mock(autospec=Protocol)` for protocols
   - **Integration tests**: Use real implementations

### Benefits of Protocol-Based Interface Adapters:

✅ **Interface adapters are testable in isolation**
- Can test `QBittorrentClient` without installing qBittorrent
- Use `Mock(autospec=QBittorrentClientProtocol)` in tests

✅ **Easy to swap external libraries**
- Want to switch from qbittorrent-api to another library?
- Create new protocol, implement adapter, inject at composition root
- Use cases don't change

✅ **Clear contracts**
- Protocol explicitly defines what methods the external library must provide
- IDE autocomplete and type checking work perfectly

✅ **No test coupling to implementation details**
- Tests depend on protocols, not concrete external libraries
- More maintainable test suite

✅ **Simple, effective mocking**
- Use `Mock(autospec=Protocol)` to ensure type safety
- Mock return values and verify method calls
- No need to create custom mock classes

### Configuration Management

Configuration lives in the **infrastructure layer** and handles loading settings from environment variables, config files, or defaults.

**Location:** `src/infrastructure/config/config.py`

**Config File Location:** `~/.torrent-cli/config.toml` (or `.env` file)

```python
# src/infrastructure/config/config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os
import tomllib  # Python 3.11+

@dataclass(frozen=True)
class Config:
    """Application configuration"""
    
    # Database
    db_path: Path
    
    # qBittorrent
    qbt_host: str
    qbt_port: int
    qbt_username: str
    qbt_password: str
    
    # Download settings
    default_download_dir: Path
    
    @classmethod
    def load(cls) -> "Config":
        """
        Load configuration from multiple sources (priority order):
        1. Environment variables
        2. Config file (~/.torrent-cli/config.toml)
        3. Default values
        """
        # Get config directory
        config_dir = Path.home() / ".torrent-cli"
        config_file = config_dir / "config.toml"
        
        # Load from config file if exists
        file_config = {}
        if config_file.exists():
            with open(config_file, "rb") as f:
                file_config = tomllib.load(f)
        
        # Build config with priority: env vars > file > defaults
        return cls(
            # Database
            db_path=Path(
                os.getenv("TORRENT_CLI_DB_PATH")
                or file_config.get("database", {}).get("path")
                or str(config_dir / "downloads.db")
            ),
            
            # qBittorrent
            qbt_host=os.getenv("QBT_HOST") 
                or file_config.get("qbittorrent", {}).get("host")
                or "localhost",
            
            qbt_port=int(
                os.getenv("QBT_PORT")
                or file_config.get("qbittorrent", {}).get("port")
                or 8080
            ),
            
            qbt_username=os.getenv("QBT_USERNAME")
                or file_config.get("qbittorrent", {}).get("username")
                or "admin",
            
            qbt_password=os.getenv("QBT_PASSWORD")
                or file_config.get("qbittorrent", {}).get("password")
                or "adminpass",
            
            # Download settings
            default_download_dir=Path(
                os.getenv("TORRENT_CLI_DOWNLOAD_DIR")
                or file_config.get("downloads", {}).get("directory")
                or str(Path.home() / "Downloads")
            )
        )
    
    @classmethod
    def create_default_config_file(cls) -> Path:
        """Create a default config file at ~/.torrent-cli/config.toml"""
        config_dir = Path.home() / ".torrent-cli"
        config_file = config_dir / "config.toml"
        
        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default config content
        default_config = """# Torrent CLI Configuration

[database]
path = "~/.torrent-cli/downloads.db"

[qbittorrent]
host = "localhost"
port = 8080
username = "admin"
password = "adminpass"

[downloads]
directory = "~/Downloads"
"""
        
        # Write default config if doesn't exist
        if not config_file.exists():
            config_file.write_text(default_config)
        
        return config_file
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        # Create config directory
        config_dir = Path.home() / ".torrent-cli"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create database directory
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create default download directory
        self.default_download_dir.mkdir(parents=True, exist_ok=True)
```

**Example config.toml file:**
```toml
# ~/.torrent-cli/config.toml

[database]
path = "~/.torrent-cli/downloads.db"

[qbittorrent]
host = "localhost"
port = 8080
username = "admin"
password = "adminpass"

[downloads]
directory = "~/Downloads"
```

**Example .env file (alternative):**
```bash
# .env or environment variables
TORRENT_CLI_DB_PATH=/home/user/.torrent-cli/downloads.db
QBT_HOST=localhost
QBT_PORT=8080
QBT_USERNAME=admin
QBT_PASSWORD=adminpass
TORRENT_CLI_DOWNLOAD_DIR=/home/user/Downloads
```

**Config Instantiation:**

The config is loaded **once** at application startup in the DI container:

```python
# src/infrastructure/di/container.py

class Container:
    """Dependency injection container"""
    
    def __init__(self):
        # Load config once at startup
        self._config = Config.load()
        self._config.ensure_directories()
        
        # Initialize all dependencies
        self._repository = None
        self._torrent_client = None
        self._aggregator = None
    
    @property
    def config(self) -> Config:
        """Get application config"""
        return self._config
    
    # ... rest of container methods
```

**First-time Setup:**

The CLI can create a default config on first run:

```python
# src/infrastructure/cli/main.py

import typer

app = typer.Typer(name="torrent-cli", help="CLI Torrent Download Manager")

@app.command()
def init():
    """Initialize configuration"""
    config_file = Config.create_default_config_file()
    typer.echo(f"Created config file at: {config_file}")
    typer.echo("Edit this file to configure qBittorrent connection")

# Usage: torrent-cli init
```

---

## Request/Response Models and Controllers

Controllers use **Request and Response Models** (Pydantic) to interact with any presentation layer. These models are framework-agnostic and can be reused across CLI, Web API, GUI, or any other interface.

### Architecture Layers:

```
Presentation Layer (Typer CLI)
    ↓
Request Model (Pydantic - validates input)
    ↓
Controller (Infrastructure - presentation-agnostic)
    ↓
Use Case InputData DTO (Application)
    ↓
Use Case (Application - business logic)
    ↓
Use Case OutputData DTO (Application)
    ↓
Controller (Infrastructure - converts)
    ↓
Response Model (Pydantic - structured output)
    ↓
Presentation Layer (formats & displays)
```

### Why Request/Response Models?

**Separation of Concerns:**
- **Request Models** - Validate and structure incoming data from ANY presentation (CLI, Web, GUI)
- **Response Models** - Structure outgoing data in a presentation-agnostic format
- **Controllers** - Presentation-agnostic, convert between Request/Response and Use Case DTOs
- **Presentation Layer** - Framework-specific, handles routing and display

### Benefits:

✅ **Validation** - Pydantic validates types, required fields, formats automatically
✅ **Reusable** - Same models/controllers work for CLI, Web API, GUI
✅ **Framework Agnostic** - No dependency on Typer, FastAPI, or any framework
✅ **Type Safe** - Full type hints and IDE support
✅ **Testable** - Easy to test controllers with Request/Response models
✅ **Clear Contract** - Explicit interface between presentation and business logic

### Project Structure Update:

```
src/infrastructure/
├── controllers/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py  # Pydantic Request Models
│   │   └── responses.py # Pydantic Response Models
│   ├── search_controller.py
│   ├── download_controller.py
│   └── ...
├── cli/
│   ├── __init__.py
│   ├── main.py
│   └── commands/
│       ├── search.py  # Uses Request/Response models
│       ├── download.py
│       └── ...
```

Now the document is structured properly with pydantic dependency and Request/Response models.

### Request Models (Pydantic)

**Location:** `src/infrastructure/controllers/models/requests.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid

class SearchTorrentsRequest(BaseModel):
    """Request model for searching torrents"""
    query: str = Field(..., min_length=1, description="Search query")
    sources: Optional[list[str]] = Field(default=None, description="Aggregator sources")
    max_results: int = Field(default=10, ge=1, le=100, description="Max results per source")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

class AddDownloadRequest(BaseModel):
    """Request model for adding a download"""
    magnet_link: str = Field(..., description="Magnet link")
    title: str = Field(..., min_length=1, description="Download title")
    source: str = Field(..., min_length=1, description="Source aggregator")
    size: str = Field(..., description="File size")
    download_directory: Optional[str] = Field(default=None, description="Download directory")
    
    @field_validator('magnet_link')
    @classmethod
    def validate_magnet_link(cls, v: str) -> str:
        if not v.startswith("magnet:?"):
            raise ValueError("Invalid magnet link format")
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        return v.strip()

class ListDownloadsRequest(BaseModel):
    """Request model for listing downloads"""
    status: Optional[str] = Field(default=None, description="Filter by status")
    sort_by: str = Field(default="date_added", description="Sort field")
    ascending: bool = Field(default=False, description="Sort ascending")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["DOWNLOADING", "COMPLETED", "FAILED", "PAUSED"]
            if v.upper() not in allowed:
                raise ValueError(f"Status must be one of: {allowed}")
            return v.upper()
        return v

class GetDownloadStatusRequest(BaseModel):
    """Request model for getting download status"""
    download_id: str = Field(..., description="Download ID (UUID)")
    
    @field_validator('download_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format")
        return v

class RemoveDownloadRequest(BaseModel):
    """Request model for removing a download"""
    download_id: str = Field(..., description="Download ID (UUID)")
    delete_files: bool = Field(default=False, description="Delete files from disk")
    
    @field_validator('download_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format")
        return v
```

### Response Models (Pydantic)

**Location:** `src/infrastructure/controllers/models/responses.py`

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TorrentSearchResultResponse(BaseModel):
    """Response model for a single search result"""
    title: str
    size: str
    seeders: int
    leechers: int
    source: str
    magnet_link: str
    date_found: datetime

class SearchTorrentsResponse(BaseModel):
    """Response model for search results"""
    results: list[TorrentSearchResultResponse]
    total_count: int

class DownloadResponse(BaseModel):
    """Response model for a download"""
    id: str
    magnet_link: str
    title: str
    file_path: str
    source: str
    status: str
    date_added: datetime
    date_completed: Optional[datetime]
    size: str

class AddDownloadResponse(BaseModel):
    """Response model for adding a download"""
    download: DownloadResponse
    message: str = "Download added successfully"

class ListDownloadsResponse(BaseModel):
    """Response model for listing downloads"""
    downloads: list[DownloadResponse]
    total_count: int

class DownloadStatusResponse(BaseModel):
    """Response model for download status"""
    download: DownloadResponse
    progress: float
    download_rate: str
    upload_rate: str
    eta: str

class RemoveDownloadResponse(BaseModel):
    """Response model for removing a download"""
    success: bool
    download_id: str
    message: str

class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    error_type: str
    details: Optional[str] = None
```

### Controllers (Presentation-Agnostic)

**Location:** `src/infrastructure/controllers/search_controller.py`

```python
from src.application.use_cases.search_torrents import SearchTorrentsUseCase
from src.infrastructure.controllers.models.requests import SearchTorrentsRequest
from src.infrastructure.controllers.models.responses import (
    SearchTorrentsResponse,
    TorrentSearchResultResponse,
    ErrorResponse
)
from src.domain.exceptions import ValidationError, AggregatorError

class SearchController:
    """
    Controller for search operations.
    
    This controller is presentation-agnostic and can be used by:
    - CLI (Typer)
    - Web API (FastAPI)
    - GUI (Qt, Tkinter)
    - gRPC service
    - Any other presentation layer
    """
    
    def __init__(self, search_use_case: SearchTorrentsUseCase):
        self.search_use_case = search_use_case
    
    def search(
        self, 
        request: SearchTorrentsRequest
    ) -> SearchTorrentsResponse | ErrorResponse:
        """
        Handle search request.
        
        Args:
            request: Validated search request (Pydantic model)
            
        Returns:
            SearchTorrentsResponse on success, ErrorResponse on error
        """
        try:
            # Convert Request Model to Use Case InputData
            input_data = SearchTorrentsUseCase.InputData(
                query=request.query,
                aggregator_names=request.sources,
                max_results=request.max_results
            )
            
            # Execute use case
            output_data = self.search_use_case.execute(input_data)
            
            # Convert Use Case OutputData to Response Model
            results = [
                TorrentSearchResultResponse(
                    title=result.title,
                    size=result.size,
                    seeders=result.seeders,
                    leechers=result.leechers,
                    source=result.source,
                    magnet_link=result.magnet_link,
                    date_found=result.date_found
                )
                for result in output_data.results
            ]
            
            return SearchTorrentsResponse(
                results=results,
                total_count=len(results)
            )
            
        except ValidationError as e:
            return ErrorResponse(
                error=str(e),
                error_type="ValidationError",
                details="Invalid input provided"
            )
        except AggregatorError as e:
            return ErrorResponse(
                error=str(e),
                error_type="AggregatorError",
                details="Failed to search torrents"
            )
        except Exception as e:
            return ErrorResponse(
                error=str(e),
                error_type="UnexpectedError",
                details="An unexpected error occurred"
            )
```

**Location:** `src/infrastructure/controllers/download_controller.py`

```python
from src.application.use_cases.add_download import AddDownloadUseCase
from src.application.use_cases.list_downloads import ListDownloadsUseCase
from src.application.use_cases.get_download_status import GetDownloadStatusUseCase
from src.application.use_cases.remove_download import RemoveDownloadUseCase
from src.infrastructure.controllers.models.requests import (
    AddDownloadRequest,
    ListDownloadsRequest,
    GetDownloadStatusRequest,
    RemoveDownloadRequest
)
from src.infrastructure.controllers.models.responses import (
    AddDownloadResponse,
    ListDownloadsResponse,
    DownloadStatusResponse,
    RemoveDownloadResponse,
    DownloadResponse,
    ErrorResponse
)
from src.domain.exceptions import (
    ValidationError,
    DuplicateDownloadError,
    DownloadNotFoundError,
    TorrentClientError
)

class DownloadController:
    """Controller for download operations (presentation-agnostic)"""
    
    def __init__(
        self,
        add_download_use_case: AddDownloadUseCase,
        list_downloads_use_case: ListDownloadsUseCase,
        get_status_use_case: GetDownloadStatusUseCase,
        remove_download_use_case: RemoveDownloadUseCase
    ):
        self.add_download_use_case = add_download_use_case
        self.list_downloads_use_case = list_downloads_use_case
        self.get_status_use_case = get_status_use_case
        self.remove_download_use_case = remove_download_use_case
    
    def add_download(
        self, 
        request: AddDownloadRequest
    ) -> AddDownloadResponse | ErrorResponse:
        """Handle add download request"""
        try:
            input_data = AddDownloadUseCase.InputData(
                magnet_link=request.magnet_link,
                title=request.title,
                source=request.source,
                size=request.size,
                download_directory=request.download_directory
            )
            
            output_data = self.add_download_use_case.execute(input_data)
            
            download = DownloadResponse(
                id=output_data.download.id,
                magnet_link=output_data.download.magnet_link,
                title=output_data.download.title,
                file_path=output_data.download.file_path,
                source=output_data.download.source,
                status=output_data.download.status,
                date_added=output_data.download.date_added,
                date_completed=output_data.download.date_completed,
                size=output_data.download.size
            )
            
            return AddDownloadResponse(download=download)
            
        except ValidationError as e:
            return ErrorResponse(error=str(e), error_type="ValidationError")
        except DuplicateDownloadError as e:
            return ErrorResponse(error=str(e), error_type="DuplicateDownloadError")
        except TorrentClientError as e:
            return ErrorResponse(error=str(e), error_type="TorrentClientError")
        except Exception as e:
            return ErrorResponse(error=str(e), error_type="UnexpectedError")
    
    def list_downloads(
        self, 
        request: ListDownloadsRequest
    ) -> ListDownloadsResponse | ErrorResponse:
        """Handle list downloads request"""
        try:
            input_data = ListDownloadsUseCase.InputData(
                status=request.status,
                sort_by=request.sort_by,
                ascending=request.ascending
            )
            
            output_data = self.list_downloads_use_case.execute(input_data)
            
            downloads = [
                DownloadResponse(
                    id=download.id,
                    magnet_link=download.magnet_link,
                    title=download.title,
                    file_path=download.file_path,
                    source=download.source,
                    status=download.status,
                    date_added=download.date_added,
                    date_completed=download.date_completed,
                    size=download.size
                )
                for download in output_data.downloads
            ]
            
            return ListDownloadsResponse(
                downloads=downloads,
                total_count=len(downloads)
            )
            
        except ValidationError as e:
            return ErrorResponse(error=str(e), error_type="ValidationError")
        except Exception as e:
            return ErrorResponse(error=str(e), error_type="UnexpectedError")
    
    def get_status(
        self, 
        request: GetDownloadStatusRequest
    ) -> DownloadStatusResponse | ErrorResponse:
        """Handle get status request"""
        try:
            input_data = GetDownloadStatusUseCase.InputData(
                download_id=request.download_id
            )
            
            output_data = self.get_status_use_case.execute(input_data)
            
            download = DownloadResponse(
                id=output_data.download.id,
                magnet_link=output_data.download.magnet_link,
                title=output_data.download.title,
                file_path=output_data.download.file_path,
                source=output_data.download.source,
                status=output_data.download.status,
                date_added=output_data.download.date_added,
                date_completed=output_data.download.date_completed,
                size=output_data.download.size
            )
            
            return DownloadStatusResponse(
                download=download,
                progress=output_data.progress,
                download_rate=output_data.download_rate,
                upload_rate=output_data.upload_rate,
                eta=output_data.eta
            )
            
        except ValidationError as e:
            return ErrorResponse(error=str(e), error_type="ValidationError")
        except DownloadNotFoundError as e:
            return ErrorResponse(error=str(e), error_type="DownloadNotFoundError")
        except Exception as e:
            return ErrorResponse(error=str(e), error_type="UnexpectedError")
    
    def remove_download(
        self, 
        request: RemoveDownloadRequest
    ) -> RemoveDownloadResponse | ErrorResponse:
        """Handle remove download request"""
        try:
            input_data = RemoveDownloadUseCase.InputData(
                download_id=request.download_id,
                delete_files=request.delete_files
            )
            
            output_data = self.remove_download_use_case.execute(input_data)
            
            return RemoveDownloadResponse(
                success=output_data.success,
                download_id=output_data.download_id,
                message="Download removed successfully"
            )
            
        except ValidationError as e:
            return ErrorResponse(error=str(e), error_type="ValidationError")
        except DownloadNotFoundError as e:
            return ErrorResponse(error=str(e), error_type="DownloadNotFoundError")
        except Exception as e:
            return ErrorResponse(error=str(e), error_type="UnexpectedError")
```

### CLI Commands (Using Request/Response Models)

**Location:** `src/infrastructure/cli/commands/search.py`

```python
import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from pydantic import ValidationError as PydanticValidationError

from src.infrastructure.controllers.search_controller import SearchController
from src.infrastructure.controllers.models.requests import SearchTorrentsRequest
from src.infrastructure.controllers.models.responses import ErrorResponse

app = typer.Typer()
console = Console()

def get_search_controller() -> SearchController:
    """Get search controller from DI container"""
    from src.infrastructure.di.container import container
    return container.search_controller()

@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    sources: Annotated[list[str] | None, typer.Option(help="Aggregator sources")] = None,
    max_results: Annotated[int, typer.Option(help="Max results per source")] = 10
):
    """Search for torrents"""
    controller = get_search_controller()
    
    try:
        # Create Request Model from CLI input (Pydantic validates)
        request = SearchTorrentsRequest(
            query=query,
            sources=sources,
            max_results=max_results
        )
        
        # Call controller with Request Model
        response = controller.search(request)
        
        # Handle Response Model
        if isinstance(response, ErrorResponse):
            console.print(f"[red]Error:[/red] {response.error}")
            raise typer.Exit(code=1)
        
        if not response.results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        # Format Response Model with Rich
        table = Table(title=f"Search Results ({response.total_count} found)")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Title", style="white")
        table.add_column("Size", style="green", width=10)
        table.add_column("Seeders", style="magenta", width=8)
        table.add_column("Source", style="blue", width=12)
        
        for idx, result in enumerate(response.results, 1):
            table.add_row(
                str(idx),
                result.title,
                result.size,
                str(result.seeders),
                result.source
            )
        
        console.print(table)
        
    except PydanticValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        raise typer.Exit(code=1)
```

**Location:** `src/infrastructure/cli/commands/download.py`

```python
import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from pydantic import ValidationError as PydanticValidationError

from src.infrastructure.controllers.download_controller import DownloadController
from src.infrastructure.controllers.models.requests import (
    AddDownloadRequest,
    ListDownloadsRequest,
    GetDownloadStatusRequest
)
from src.infrastructure.controllers.models.responses import ErrorResponse

app = typer.Typer()
console = Console()

def get_download_controller() -> DownloadController:
    """Get download controller from DI container"""
    from src.infrastructure.di.container import container
    return container.download_controller()

@app.command("add")
def add_download(
    magnet_link: Annotated[str, typer.Argument(help="Magnet link")],
    title: Annotated[str, typer.Option(help="Download title")],
    source: Annotated[str, typer.Option(help="Source aggregator")],
    size: Annotated[str, typer.Option(help="File size")],
    directory: Annotated[str | None, typer.Option(help="Download directory")] = None
):
    """Add a download"""
    controller = get_download_controller()
    
    try:
        request = AddDownloadRequest(
            magnet_link=magnet_link,
            title=title,
            source=source,
            size=size,
            download_directory=directory
        )
        
        response = controller.add_download(request)
        
        if isinstance(response, ErrorResponse):
            console.print(f"[red]Error:[/red] {response.error}")
            raise typer.Exit(code=1)
        
        console.print(f"[green]✓[/green] {response.message}")
        console.print(f"  Title: {response.download.title}")
        console.print(f"  ID: {response.download.id}")
        console.print(f"  Status: {response.download.status}")
        console.print(f"  Path: {response.download.file_path}")
        
    except PydanticValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        raise typer.Exit(code=1)

@app.command("list")
def list_downloads(
    status: Annotated[str | None, typer.Option(help="Filter by status")] = None,
    sort_by: Annotated[str, typer.Option(help="Sort field")] = "date_added",
    ascending: Annotated[bool, typer.Option(help="Sort ascending")] = False
):
    """List all downloads"""
    controller = get_download_controller()
    
    try:
        request = ListDownloadsRequest(
            status=status,
            sort_by=sort_by,
            ascending=ascending
        )
        
        response = controller.list_downloads(request)
        
        if isinstance(response, ErrorResponse):
            console.print(f"[red]Error:[/red] {response.error}")
            raise typer.Exit(code=1)
        
        if not response.downloads:
            console.print("[yellow]No downloads found[/yellow]")
            return
        
        table = Table(title=f"Downloads ({response.total_count} total)")
        table.add_column("ID", style="cyan", width=36)
        table.add_column("Title", style="white")
        table.add_column("Status", style="green", width=12)
        table.add_column("Size", style="magenta", width=10)
        
        for download in response.downloads:
            table.add_row(
                download.id,
                download.title,
                download.status,
                download.size
            )
        
        console.print(table)
        
    except PydanticValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        raise typer.Exit(code=1)
```

### Alternative Presentation Example (FastAPI)

Controllers are presentation-agnostic, so adding a Web API is trivial:

```python
# src/infrastructure/api/main.py (hypothetical)

from fastapi import FastAPI
from src.infrastructure.controllers.search_controller import SearchController
from src.infrastructure.controllers.models.requests import SearchTorrentsRequest
from src.infrastructure.controllers.models.responses import (
    SearchTorrentsResponse,
    ErrorResponse
)

app = FastAPI()

@app.post("/api/search", response_model=SearchTorrentsResponse | ErrorResponse)
def api_search(request: SearchTorrentsRequest):
    """
    Web API endpoint - uses same controller as CLI!
    FastAPI automatically:
    - Validates request (Pydantic)
    - Serializes response to JSON (Pydantic)
    """
    controller = get_search_controller()
    return controller.search(request)
```

### Key Architectural Points:

✅ **Controllers are in infrastructure layer** - They're presentation adapters
✅ **Request/Response models are framework-agnostic** - Just Pydantic, no Typer/FastAPI
✅ **CLI commands are thin** - Just routing + formatting
✅ **Controllers are reusable** - Work with any presentation layer
✅ **Clear separation** - Presentation → Request → Controller → Use Case → Response → Presentation



### Example Controller Pattern:

```python
# ============================================
# Controller - Infrastructure Layer
# ============================================
# Located in: src/infrastructure/controllers/search_controller.py

from src.application.use_cases.search_torrents import SearchTorrentsUseCase
from src.domain.exceptions import ValidationError, AggregatorError

class SearchController:
    """Controller for search-related operations"""
    
    def __init__(self, search_use_case: SearchTorrentsUseCase):
        self.search_use_case = search_use_case
    
    def search(
        self,
        query: str,
        sources: list[str] | None = None,
        max_results: int = 10
    ) -> list[dict] | None:
        """
        Handle search command.
        
        Returns:
            List of search results as dicts, or None if error
            
        Raises:
            ValidationError: If input is invalid
            AggregatorError: If search fails
        """
        # Convert CLI input to use case InputData
        input_data = SearchTorrentsUseCase.InputData(
            query=query,
            aggregator_names=sources,
            max_results=max_results
        )
        
        # Execute use case
        output_data = self.search_use_case.execute(input_data)
        
        # Convert DTOs to dicts for CLI layer
        return [
            {
                'title': result.title,
                'size': result.size,
                'seeders': result.seeders,
                'leechers': result.leechers,
                'source': result.source,
                'magnet_link': result.magnet_link
            }
            for result in output_data.results
        ]

# ============================================
# Controller - Add Download Example
# ============================================
# Located in: src/infrastructure/controllers/download_controller.py

class DownloadController:
    """Controller for download-related operations"""
    
    def __init__(
        self,
        add_download_use_case: AddDownloadUseCase,
        list_downloads_use_case: ListDownloadsUseCase,
        get_status_use_case: GetDownloadStatusUseCase,
    ):
        self.add_download_use_case = add_download_use_case
        self.list_downloads_use_case = list_downloads_use_case
        self.get_status_use_case = get_status_use_case
    
    def add_download(
        self,
        magnet_link: str,
        title: str,
        source: str,
        size: str,
        download_directory: str | None = None
    ) -> dict:
        """
        Handle add download command.
        
        Returns:
            Download info as dict
            
        Raises:
            ValidationError, DuplicateDownloadError, TorrentClientError
        """
        input_data = AddDownloadUseCase.InputData(
            magnet_link=magnet_link,
            title=title,
            source=source,
            size=size,
            download_directory=download_directory
        )
        
        output_data = self.add_download_use_case.execute(input_data)
        
        # Convert DTO to dict
        return {
            'id': output_data.download.id,
            'title': output_data.download.title,
            'status': output_data.download.status,
            'file_path': output_data.download.file_path,
            'size': output_data.download.size,
            'source': output_data.download.source
        }
    
    def list_downloads(
        self,
        status: str | None = None,
        sort_by: str = "date_added",
        ascending: bool = False
    ) -> list[dict]:
        """
        Handle list downloads command.
        
        Returns:
            List of downloads as dicts
        """
        input_data = ListDownloadsUseCase.InputData(
            status=status,
            sort_by=sort_by,
            ascending=ascending
        )
        
        output_data = self.list_downloads_use_case.execute(input_data)
        
        return [
            {
                'id': download.id,
                'title': download.title,
                'status': download.status,
                'size': download.size,
                'source': download.source,
                'file_path': download.file_path
            }
            for download in output_data.downloads
        ]
    
    def get_status(self, download_id: str) -> dict:
        """
        Handle get status command.
        
        Returns:
            Status info as dict
        """
        input_data = GetDownloadStatusUseCase.InputData(
            download_id=download_id
        )
        
        output_data = self.get_status_use_case.execute(input_data)
        
        return {
            'download': {
                'id': output_data.download.id,
                'title': output_data.download.title,
                'status': output_data.download.status
            },
            'progress': output_data.progress,
            'download_rate': output_data.download_rate,
            'upload_rate': output_data.upload_rate,
            'eta': output_data.eta
        }

# ============================================
# CLI Commands - Infrastructure Layer
# ============================================
# Located in: src/infrastructure/cli/commands/search.py

import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

app = typer.Typer()
console = Console()

def get_search_controller() -> SearchController:
    """Get search controller from DI container"""
    from src.infrastructure.di.container import container
    return container.search_controller()

@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    sources: Annotated[list[str] | None, typer.Option(help="Aggregator sources")] = None,
    max_results: Annotated[int, typer.Option(help="Max results per source")] = 10
):
    """Search for torrents"""
    controller = get_search_controller()
    
    try:
        results = controller.search(query=query, sources=sources, max_results=max_results)
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        # Format output with Rich
        table = Table(title="Search Results")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Title", style="white")
        table.add_column("Size", style="green", width=10)
        table.add_column("Seeders", style="magenta", width=8)
        table.add_column("Source", style="blue", width=12)
        
        for idx, result in enumerate(results, 1):
            table.add_row(
                str(idx),
                result['title'],
                result['size'],
                str(result['seeders']),
                result['source']
            )
        
        console.print(table)
        
    except ValidationError as e:
        console.print(f"[red]Error:[/red] Invalid input: {e}")
        raise typer.Exit(code=1)
    except AggregatorError as e:
        console.print(f"[red]Error:[/red] Search failed: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] Unexpected error: {e}")
        raise typer.Exit(code=1)

# ============================================
# CLI Commands - Download
# ============================================
# Located in: src/infrastructure/cli/commands/download.py

import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

app = typer.Typer()
console = Console()

def get_download_controller() -> DownloadController:
    """Get download controller from DI container"""
    from src.infrastructure.di.container import container
    return container.download_controller()

@app.command("add")
def add_download(
    magnet_link: Annotated[str, typer.Argument(help="Magnet link")],
    title: Annotated[str, typer.Option(help="Download title")],
    source: Annotated[str, typer.Option(help="Source aggregator")],
    size: Annotated[str, typer.Option(help="File size")],
    directory: Annotated[str | None, typer.Option(help="Download directory")] = None
):
    """Add a download"""
    controller = get_download_controller()
    
    try:
        download = controller.add_download(
            magnet_link=magnet_link,
            title=title,
            source=source,
            size=size,
            download_directory=directory
        )
        
        # Format output
        console.print(f"[green]✓[/green] Download added: {download['title']}")
        console.print(f"  ID: {download['id']}")
        console.print(f"  Status: {download['status']}")
        console.print(f"  Path: {download['file_path']}")
        
    except ValidationError as e:
        console.print(f"[red]Error:[/red] Invalid input: {e}")
        raise typer.Exit(code=1)
    except DuplicateDownloadError as e:
        console.print(f"[red]Error:[/red] Duplicate: {e}")
        raise typer.Exit(code=1)
    except TorrentClientError as e:
        console.print(f"[red]Error:[/red] Client error: {e}")
        raise typer.Exit(code=1)

@app.command("list")
def list_downloads(
    status: Annotated[str | None, typer.Option(help="Filter by status")] = None,
    sort_by: Annotated[str, typer.Option(help="Sort field")] = "date_added",
    ascending: Annotated[bool, typer.Option(help="Sort ascending")] = False
):
    """List all downloads"""
    controller = get_download_controller()
    
    try:
        downloads = controller.list_downloads(status=status, sort_by=sort_by, ascending=ascending)
        
        if not downloads:
            console.print("[yellow]No downloads found[/yellow]")
            return
        
        # Format output
        table = Table(title="Downloads")
        table.add_column("ID", style="cyan", width=36)
        table.add_column("Title", style="white")
        table.add_column("Status", style="green", width=12)
        table.add_column("Size", style="magenta", width=10)
        
        for download in downloads:
            table.add_row(
                download['id'],
                download['title'],
                download['status'],
                download['size']
            )
        
        console.print(table)
        
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

@app.command("status")
def get_status(
    download_id: Annotated[str, typer.Argument(help="Download ID")]
):
    """Get download status"""
    controller = get_download_controller()
    
    try:
        status_info = controller.get_status(download_id=download_id)
        
        # Format output
        download = status_info['download']
        console.print(f"[bold]{download['title']}[/bold]")
        console.print(f"Status: {download['status']}")
        console.print(f"Progress: {status_info['progress']:.2f}%")
        console.print(f"Download: {status_info['download_rate']}")
        console.print(f"Upload: {status_info['upload_rate']}")
        console.print(f"ETA: {status_info['eta']}")
        
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except DownloadNotFoundError as e:
        console.print(f"[red]Error:[/red] Not found: {e}")
        raise typer.Exit(code=1)

# ============================================
# Main CLI App - Infrastructure Layer
# ============================================
# Located in: src/infrastructure/cli/main.py

import typer
from src.infrastructure.cli.commands import search, download
from src.infrastructure.config.config import Config

app = typer.Typer(name="torrent-cli", help="CLI Torrent Download Manager")

# Register command groups
app.add_typer(search.app, name="search", help="Search for torrents")
app.add_typer(download.app, name="download", help="Manage downloads")

@app.command()
def init():
    """Initialize configuration"""
    config_file = Config.create_default_config_file()
    typer.echo(f"Created config file at: {config_file}")
    typer.echo("Edit this file to configure qBittorrent connection")

if __name__ == "__main__":
    app()
```

### Controller Benefits:

✅ **Separation of Concerns**
- CLI commands focus on routing, argument parsing, and formatting
- Controllers handle business workflow and error conversion
- Use cases remain pure business logic

✅ **Testable**
- Controllers can be tested without Typer
- Mock use cases
- Test error handling separately

✅ **Reusable**
- Same controller could work with different CLI frameworks
- Controllers return simple dicts that any interface can use

✅ **Clean Error Handling**
- Controllers catch domain exceptions
- CLI layer decides how to display errors
- Separation between error occurrence and error presentation

### Flow Summary:

```
User CLI Input
    ↓
Typer Command (routing, argument parsing)
    ↓
Controller (input conversion, error handling)
    ↓
Use Case InputData DTO
    ↓
Use Case (business logic)
    ↓
Use Case OutputData DTO
    ↓
Controller (catches exceptions, returns dict)
    ↓
Typer Command (formats with Rich, displays)
    ↓
Terminal Output
```

---

## Project Structure

```
torrent-cli/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── download.py
│   │   │   ├── torrent_search_result.py
│   │   │   └── user_preferences.py
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── magnet_link.py
│   │   │   ├── file_size.py
│   │   │   ├── aggregator_source.py
│   │   │   └── file_path.py (type alias)
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── download_repository.py (IDownloadRepository interface)
│   │   │   └── user_preferences_repository.py (IUserPreferencesRepository interface)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── aggregator_service.py (IAggregatorService interface)
│   │   │   └── torrent_client.py (ITorrentClient interface)
│   │   └── exceptions.py
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── __init__.py
│   │   │   └── shared_dtos.py (DownloadDTO, TorrentSearchResultDTO, UserPreferencesDTO)
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── search_torrents.py
│   │       ├── add_download.py
│   │       ├── list_downloads.py
│   │       ├── get_download_status.py
│   │       ├── remove_download.py
│   │       ├── pause_download.py
│   │       ├── resume_download.py
│   │       ├── refresh_downloads.py
│   │       ├── get_user_preferences.py
│   │       ├── update_user_preferences.py
│   │       ├── add_favorite_path.py
│   │       ├── remove_favorite_path.py
│   │       ├── add_favorite_aggregator.py
│   │       └── remove_favorite_aggregator.py
│   ├── interface_adapters/
│   │   ├── protocols/
│   │   │   ├── __init__.py
│   │   │   ├── qbittorrent_protocol.py
│   │   │   ├── sqlalchemy_protocol.py
│   │   │   └── torrent_search_protocol.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── sqlite_download_repository.py
│   │   │   ├── sqlite_user_preferences_repository.py
│   │   │   └── models.py (SQLAlchemy models for Download and UserPreferences)
│   │   ├── torrent_clients/
│   │   │   ├── __init__.py
│   │   │   └── qbittorrent_client.py
│   │   └── aggregators/
│   │       ├── __init__.py
│   │       └── torrent_search_aggregator.py
│   └── infrastructure/
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py (entry point, Typer app)
│       │   └── commands/
│       │       ├── __init__.py
│       │       ├── search.py (Typer command definitions + Rich formatting)
│       │       ├── download.py
│       │       ├── list.py
│       │       ├── status.py
│       │       └── remove.py
│       ├── controllers/
│       │   ├── __init__.py
│       │   ├── search_controller.py
│       │   ├── download_controller.py
│       │   ├── list_controller.py
│       │   ├── status_controller.py
│       │   └── remove_controller.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── config.py
│       └── di/
│           ├── __init__.py
│           └── container.py (dependency injection container)
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   │   ├── test_entities.py
│   │   │   └── test_value_objects.py
│   │   ├── application/
│   │   │   └── test_use_cases.py
│   │   └── interface_adapters/
│   │       ├── test_repositories.py
│   │       ├── test_torrent_clients.py
│   │       └── test_aggregators.py
│   ├── integration/
│   │   └── test_end_to_end.py
│   └── conftest.py
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── domain.md
│   │   ├── application.md
│   │   ├── interface-adapters.md
│   │   └── infrastructure.md
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
├── .env.example
├── .gitignore
└── ruff.toml (optional, can use pyproject.toml)
```

### Layer Responsibilities:

**Domain Layer** (`src/domain/`)
- Entities, Value Objects
- Interface definitions using ABC (IDownloadRepository, ITorrentClient, IAggregatorService)
- Domain exceptions
- **No dependencies on other layers**
- **No external library dependencies** (except standard library)
- **Most stable layer** - rarely changes

**Application Layer** (`src/application/`)
- Use cases (business logic orchestration)
- DTOs (data transfer objects)
- **Depends only on domain layer interfaces (ABC)**
- **No knowledge of interface adapters or infrastructure**
- **No knowledge of protocols**
- **Changes when business requirements change**

**Interface Adapters Layer** (`src/interface_adapters/`)
- **Protocols** - Define contracts for external libraries (typing.Protocol)
- **Concrete implementations** of domain interfaces (ABC)
- Database models and repositories (SQLAlchemy)
- External service adapters (qBittorrent, torrent-search-python)
- **Depends on domain layer (implements ABC interfaces)**
- **Receives external dependencies via Protocol-typed constructors**
- **Converts between domain and external formats**
- **No CLI code, no dependency injection, no framework setup**

**Infrastructure Layer** (`src/infrastructure/`)
- **CLI commands** (Typer) - Routing, argument parsing, and output formatting with Rich
- **Controllers** - Convert CLI input to DTOs, call use cases, handle errors, return structured data
- **Configuration** - Load and manage application config from files/env vars
- **Composition root** - Wires up all dependencies in DI container
- **Dependency injection container**
- **Only place where concrete external library objects are created**
- **Depends on all other layers**
- **All framework-specific code lives here**

**Flow within Infrastructure Layer:**
```
CLI Command → Controller → Use Case → Controller → CLI Command (formats & displays)
```

---

## Technology Suggestions (TBD)

---

## Questions to Consider

1. Should we track torrent metadata separately from the actual download?
2. Do we need to support multiple simultaneous downloads?
3. Should we cache search results locally?
4. Do we need download progress tracking in real-time?
5. Should we support categories/tags for organizing downloads?

---

*This document will evolve as the project develops. Keep it updated with architectural decisions and entity changes.*