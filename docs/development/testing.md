# Testing Guide

## 100% Test Coverage Mandate

**Every piece of code must have tests. This is NON-NEGOTIABLE.**

### Coverage Requirements

- ✅ **Domain Layer:** 100% - Pure logic, easy to test
- ✅ **Application Layer:** 100% - Use `Mock(spec=Interface)`
- ✅ **Interface Adapters:** 100% - Use `Mock(spec=Protocol)`
- ✅ **Infrastructure Layer:** 100% - Integration tests where appropriate

**No exceptions. No excuses.**

---

## Test Style: Plain Functions

**Use plain pytest functions, NOT test classes.**

```python
# ✅ CORRECT - Plain functions
def test_magnet_link_extracts_info_hash() -> None:
    """Should extract info hash from magnet link."""
    magnet = MagnetLink.from_string("magnet:?xt=urn:btih:abc123...")
    assert magnet.info_hash == "abc123..."

def test_magnet_link_rejects_invalid_uri() -> None:
    """Should reject invalid magnet URI."""
    with pytest.raises(ValidationError):
        MagnetLink.from_string("invalid")

# ❌ WRONG - Do NOT use test classes
class TestMagnetLink:
    def test_extracts_info_hash(self) -> None:
        ...
```

---

## Testing Strategy by Layer

### Domain Layer Tests

**Test all pure business logic:**
- Entities: All methods, business rules, validation
- Value Objects: Creation, validation, immutability
- No mocks needed (pure functions)

**Example:**
```python
def test_download_entity_creation() -> None:
    """Should create Download with valid data."""
    download = Download(
        id=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:abc123"),
        title="Test",
        file_path=FilePath("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        status=DownloadStatus.DOWNLOADING,
        date_added=datetime.now(),
        date_completed=None,
        size=FileSize.from_string("1.5 GB")
    )
    assert download.status == DownloadStatus.DOWNLOADING

def test_file_size_validates_negative() -> None:
    """Should reject negative file sizes."""
    with pytest.raises(ValidationError):
        FileSize.from_bytes(-100)
```

---

### Application Layer Tests

**Mock all dependencies with `Mock(spec=Interface)`:**

```python
from unittest.mock import Mock

def test_add_download_use_case() -> None:
    """Should add download successfully."""
    # Arrange - Mock domain interfaces (ABC)
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists.return_value = False
    mock_repo.save.return_value = Mock()  # Returns saved entity
    
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
        title="Test Download",
        source="1337x",
        size="1.5 GB"
    )
    
    # Act
    result = use_case.execute(input_data)
    
    # Assert
    assert result.download.status == "DOWNLOADING"
    mock_repo.exists.assert_called_once()
    mock_repo.save.assert_called_once()
    mock_client.add_torrent.assert_called_once()

def test_add_download_duplicate_error() -> None:
    """Should raise error for duplicate download."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists.return_value = True  # Duplicate
    
    mock_client = Mock(spec=ITorrentClient)
    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    
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
    
    with pytest.raises(DuplicateDownloadError):
        use_case.execute(input_data)
    
    # Verify client was never called
    mock_client.add_torrent.assert_not_called()
```

---

### Interface Adapters Tests

**Mock protocols with `Mock(spec=Protocol)`:**

```python
def test_qbittorrent_client_add_torrent() -> None:
    """Should add torrent via client."""
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

def test_sqlite_repository_save() -> None:
    """Should save download to database."""
    # Arrange - Mock SQLAlchemy session
    mock_session = Mock(spec=SessionProtocol)
    repo = SQLiteDownloadRepository(session=mock_session)
    
    download = Download(...)
    
    # Act
    result = repo.save(download)
    
    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
```

---

### Infrastructure Layer Tests

**Integration tests with real or mocked components:**

```python
def test_search_controller_success() -> None:
    """Should return search results."""
    # Arrange - Mock use case
    mock_use_case = Mock(spec=SearchTorrentsUseCase)
    mock_use_case.execute.return_value = SearchTorrentsUseCase.OutputData(
        results=[
            TorrentSearchResultDTO(
                title="Test",
                size="1.5 GB",
                seeders=100,
                leechers=50,
                source="1337x",
                magnet_link="magnet:?...",
                date_found=datetime.now()
            )
        ]
    )
    
    controller = SearchController(search_use_case=mock_use_case)
    
    request = SearchTorrentsRequest(
        query="ubuntu",
        max_results=10
    )
    
    # Act
    response = controller.search(request)
    
    # Assert
    assert not isinstance(response, ErrorResponse)
    assert len(response.results) == 1
    mock_use_case.execute.assert_called_once()

def test_cli_command_integration(cli_runner):
    """Integration test for CLI command."""
    result = cli_runner.invoke(app, ["search", "ubuntu"])
    assert result.exit_code == 0
    assert "Search Results" in result.output
```

---

## Test Coverage Tools

```bash
# Install
uv add --dev pytest pytest-cov

# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Fail if coverage below 100%
pytest --cov=src --cov-fail-under=100
```

---

## Test-Driven Development (TDD)

**Recommended workflow:**

1. ✅ Write test first (Red)
2. ✅ Write minimal code to pass (Green)
3. ✅ Refactor (Refactor)
4. ✅ Repeat

**Benefits:**
- Forces you to think about API design
- Ensures testable code
- Built-in regression tests
- 100% coverage by default

---

## Common Testing Patterns

### Testing Exceptions

```python
def test_raises_validation_error() -> None:
    """Should raise ValidationError for invalid input."""
    with pytest.raises(ValidationError, match="Invalid magnet link"):
        MagnetLink.from_string("invalid")
```

### Testing with Fixtures

```python
@pytest.fixture
def mock_repository():
    """Fixture for mocked repository."""
    repo = Mock(spec=IDownloadRepository)
    repo.exists.return_value = False
    return repo

def test_with_fixture(mock_repository) -> None:
    """Should use fixture."""
    use_case = AddDownloadUseCase(repository=mock_repository, ...)
    # Test here
```

### Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_operation() -> None:
    """Should handle async operation."""
    result = await some_async_function()
    assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("size_str,expected_bytes", [
    ("1 KB", 1024),
    ("1.5 MB", 1572864),
    ("2 GB", 2147483648),
])
def test_file_size_parsing(size_str: str, expected_bytes: int) -> None:
    """Should parse various size formats."""
    size = FileSize.from_string(size_str)
    assert size.bytes == expected_bytes
```

---

## Testing Checklist

Before committing:

```bash
# 1. Format code
ruff format .

# 2. Check linting
ruff check --fix .

# 3. Run tests with coverage
pytest --cov=src --cov-fail-under=100

# 4. Check coverage report
open htmlcov/index.html
```

---

## No Excuses Policy

❌ **"It's just a simple getter"** → **Test it**
❌ **"It's just wiring code"** → **Test it**
❌ **"It's hard to test"** → **Refactor to make it testable**
❌ **"I'll add tests later"** → **NO. Add them NOW.**

✅ **Test everything. 100% coverage. Non-negotiable.**

---

## Benefits of 100% Coverage

1. **Confidence** - Know your code works
2. **Refactoring** - Change code without fear
3. **Documentation** - Tests show how to use code
4. **Regression Prevention** - Catch breaking changes
5. **Better Design** - Forces modular, testable code

---

## Summary

- **Use plain pytest functions**, not test classes
- **Mock with `Mock(spec=Interface)` or `Mock(spec=Protocol)`**
- **Test all layers** - Domain, Application, Interface Adapters, Infrastructure
- **100% coverage required** - No exceptions
- **TDD encouraged** - Write tests first
- **Run tests before every commit**

**If it's not tested, it's broken.**
