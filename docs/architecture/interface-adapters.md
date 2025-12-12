# Interface Adapters Layer

The Interface Adapters layer implements the interfaces defined in the Application layer. It adapts data between the application's use cases and external systems. This layer contains protocols that define boundaries between layers and concrete adapters that bridge them.

## Current Status

**✅ Implemented** - Core adapters for indexer and torrent client operations are complete.

## Principles

- ✅ **Implements Application interfaces** - Concrete implementations of ABCs
- ✅ **Defines protocols** - Protocols for external service boundaries
- ✅ **Depends on Application and Domain** - Uses interfaces and entities
- ✅ **Handles data transformation** - Converts between external formats and domain entities
- ✅ **Isolated from Infrastructure** - Doesn't know about CLI or DI container

## Components

### Indexer Manager Adapters

#### ProwlarrIndexerManager

**Status:** ✅ Implemented

Concrete implementation of `IndexerManager` that provides torrent search through Prowlarr.

**Responsibilities:**
- Wraps `IProwlarrSource` (raw Prowlarr API client)
- Maps raw Prowlarr API responses to domain `TorrentSearchResult` entities
- Validates and transforms data at the infrastructure boundary
- Handles date parsing and field fallbacks

**Location**: `src/nodo/interface_adapters/adapters/prowlarr_indexer_manager.py`

**Key Methods:**
```python
def search(
    query: str,
    indexer_names: list[str] | None = None,
    max_results: int = 10,
) -> list[TorrentSearchResult]:
    """Search for torrents and return domain entities"""

def get_available_indexers(self) -> list[str]:
    """Get list of available indexers from Prowlarr"""
```

**Data Transformation:**
```
Prowlarr API JSON → Raw dict → TorrentSearchResult entities
       (raw)              (mapping)         (domain)
```

### Protocols

#### IProwlarrSource

**Status:** ✅ Implemented

Protocol defining the interface for Prowlarr source services that return raw data.

**Responsibilities:**
- Define contract for Prowlarr API clients
- Specify raw data interface (returns `list[dict[str, Any]]`)
- Serve as boundary between infrastructure (HTTP) and application (domain entities)

**Location**: `src/nodo/interface_adapters/protocols/prowlarr_source_protocol.py`

**Methods:**
```python
def search(
    query: str,
    indexer_names: list[str] | None = None,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Search for torrents, returning raw API responses"""

def get_available_indexers(self) -> list[str]:
    """Get list of available indexers"""
```

**Raises:**
- `IndexerError` - If the search fails
- `IndexerTimeoutError` - If the search times out

## Data Transformation Examples

### Prowlarr Raw Data → Domain Entity

```python
# Raw response from Prowlarr API
raw_result = {
    "magnetUrl": "magnet:?xt=urn:btih:...",
    "title": "Ubuntu 24.04",
    "size": 3221225472,
    "seeders": 150,
    "leechers": 25,
    "indexer": "1337x",
    "publishDate": "2025-06-15T14:30:45Z"
}

# Transformed to domain entity
result = TorrentSearchResult(
    magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:..."),
    title="Ubuntu 24.04",
    size=FileSize(bytes_=3221225472),
    seeders=150,
    leechers=25,
    source=IndexerSource.from_string("1337x"),  # Normalized to canonical form
    date_found=datetime(2025, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
)
```

## Error Handling

Interface adapters should:

- Catch external system errors (network, timeouts, invalid responses)
- Convert to domain exceptions when appropriate
- Handle missing or malformed fields with sensible defaults
- Skip malformed results while processing valid ones
- Provide meaningful error messages

**Example:**
```python
try:
    response = self._indexer_source.search(query, indexer_names, max_results)
except requests.Timeout:
    raise IndexerTimeoutError(f"Prowlarr search timed out after {timeout}s")
except requests.RequestException as e:
    raise IndexerError(f"Prowlarr API request failed: {e}")
```

## Testing

Interface adapters are tested with:

- **Unit tests** - Mocked external dependencies (e.g., mocked Prowlarr adapter)
- **Integration tests** - Against real external services in test environments
- **Data transformation tests** - Verify correct mapping of raw data to domain entities

**Example Test:**
```python
def test_prowlarr_index_manager_maps_raw_to_entities():
    mock_source = Mock(spec=IProwlarrSource)
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:...",
            "title": "Test",
            "size": 1024,
            "seeders": 50,
            "leechers": 5,
            "indexer": "Prowlarr",
            "publishDate": "2025-01-01T12:00:00Z"
        }
    ]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert isinstance(results[0], TorrentSearchResult)
    assert results[0].title == "Test"
```

## Future Extensibility

The architecture supports adding more indexer managers:

1. **Create new protocol** - `IJackettSource` in `protocols/`
2. **Implement adapter** - `JackettIndexerManager` in `adapters/`
3. **Register in DI** - Configure in infrastructure layer

This maintains the separation of concerns while allowing different indexer implementations.

## Current Project Structure

```
src/nodo/interface_adapters/
├── __init__.py
├── adapters/
│   ├── __init__.py
│   └── prowlarr_indexer_manager.py  # ProwlarrIndexerManager
├── protocols/
│   ├── __init__.py
│   └── prowlarr_source_protocol.py  # IProwlarrSource
```

## Key Design Decisions

1. **Separate protocols for raw data** - `IProwlarrSource` handles infrastructure boundary
2. **Adapter pattern** - `ProwlarrIndexerManager` provides domain-level interface
3. **Lazy transformation** - Only transform data when creating domain entities
4. **Fault tolerance** - Skip malformed results rather than fail entire search

## Related Documentation

- [Application Layer](application.md) - See `IndexerManager` interface
- [Domain Layer](domain.md) - See `TorrentSearchResult` entity
- [Infrastructure](infrastructure.md) - See how adapters are wired together
