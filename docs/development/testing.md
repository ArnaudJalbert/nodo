# Testing

Nodo follows a comprehensive testing strategy to ensure code quality and reliability.

## Testing Philosophy

- **100% test coverage** - All code must be tested
- **Test in isolation** - Each layer tested independently
- **Fast tests** - Unit tests should run quickly
- **Clear test names** - Test names describe what they test

## Test Structure

Tests mirror the source code structure:

```
tests/
└── nodo/
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   └── exceptions/
    ├── application/
    │   └── dtos/
    ├── interface_adapters/
    └── infrastructure/
```

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run with Coverage

```bash
uv run pytest --cov=src --cov-report=term
```

### Run with HTML Coverage Report

```bash
uv run pytest --cov=src --cov-report=html
```

Open `htmlcov/index.html` in your browser to view the report.

### Run Specific Test Suite

```bash
# Domain layer tests
uv run pytest tests/nodo/domain/

# Application layer tests
uv run pytest tests/nodo/application/
```

## Test Coverage Requirements

- **Minimum coverage**: 100%
- **Enforced in CI**: Coverage must not decrease
- **New code**: Must include tests

Check coverage:

```bash
uv run pytest --cov=src --cov-fail-under=100
```

## Writing Tests

### Domain Layer Tests

Domain tests are straightforward - no mocks needed:

```python
def test_download_creation():
    """Test creating a download entity."""
    magnet = MagnetLink("magnet:?xt=urn:btih:...")
    size = FileSize(1_500_000_000)
    source = AggregatorSource("1337x")
    
    download = Download(
        magnet_link=magnet,
        title="Test Download",
        file_path=Path("/test"),
        source=source,
        size=size
    )
    
    assert download.id_ is not None
    assert download.status == DownloadStatus.DOWNLOADING
    assert download.date_added is not None
```

### Application Layer Tests

Use mocks for dependencies:

```python
def test_add_download_use_case():
    """Test adding a download."""
    # Create mocks
    download_repo = Mock(spec=IDownloadRepository)
    torrent_client = Mock(spec=ITorrentClient)
    preferences_repo = Mock(spec=IUserPreferencesRepository)
    
    # Setup mocks
    preferences_repo.get.return_value = UserPreferences(...)
    torrent_client.add_torrent.return_value = "torrent_hash"
    download_repo.exists_by_magnet_link.return_value = False
    
    # Create use case
    use_case = AddDownload(download_repo, torrent_client, preferences_repo)
    
    # Execute
    result = use_case.execute(magnet_link, "Test")
    
    # Assert
    assert result is not None
    download_repo.save.assert_called_once()
```

### Integration Tests

Test with real dependencies:

```python
def test_download_repository_integration(tmp_path):
    """Test repository with real database."""
    db_path = tmp_path / "test.db"
    session = create_session(str(db_path))
    repo = SQLiteDownloadRepository(session)
    
    # Test operations
    download = Download(...)
    repo.save(download)
    
    found = repo.find_by_id(download.id_)
    assert found is not None
    assert found.title == download.title
```

## Test Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def sample_download():
    """Create a sample download for testing."""
    return Download(
        magnet_link=MagnetLink("magnet:?xt=urn:btih:..."),
        title="Test",
        file_path=Path("/test"),
        source=AggregatorSource("1337x"),
        size=FileSize(1000)
    )
```

## Test Naming

Follow this naming convention:

- Test files: `test_<module_name>.py`
- Test functions: `test_<what_is_tested>`

Examples:
- `test_download.py`
- `test_download_creation()`
- `test_download_status_transition()`

## Parametrized Tests

Use `@pytest.mark.parametrize` for testing multiple inputs:

```python
@pytest.mark.parametrize("size_bytes,expected", [
    (1000, "1.0 KB"),
    (1_000_000, "1.0 MB"),
    (1_000_000_000, "1.0 GB"),
])
def test_file_size_formatting(size_bytes, expected):
    """Test file size formatting."""
    size = FileSize(size_bytes)
    assert size.human_readable() == expected
```

## Testing Exceptions

Test that exceptions are raised correctly:

```python
def test_duplicate_download_raises_error():
    """Test adding duplicate download raises error."""
    download_repo = Mock(spec=IDownloadRepository)
    download_repo.exists_by_magnet_link.return_value = True
    
    use_case = AddDownload(...)
    
    with pytest.raises(DuplicateDownloadError):
        use_case.execute(magnet_link, "Test")
```

## Continuous Integration

Tests run automatically on:
- Every pull request
- Every push to main branch
- Coverage is checked and must be 100%

## Best Practices

1. **One assertion per test** (when possible) - Makes failures clear
2. **Arrange-Act-Assert** - Structure tests clearly
3. **Test edge cases** - Boundary conditions, empty inputs, etc.
4. **Test error cases** - Verify exceptions are raised
5. **Keep tests fast** - Use mocks for slow operations
6. **Test behavior, not implementation** - Test what, not how

## Next Steps

- [Development Setup](setup.md) - Set up your development environment
- [Contributing](contributing.md) - Learn how to contribute

