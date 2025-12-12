"""Tests for ProwlarrIndexerManager."""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from nodo.domain.exceptions import IndexerError, IndexerTimeoutError
from nodo.domain.value_objects import FileSize, MagnetLink
from nodo.interface_adapters import ProwlarrIndexerManager


def test_indexer_source_adapter_maps_raw_results_to_entities() -> None:
    """Should map raw indexer source results to domain entities."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Test Torrent",
            "size": 1024 * 1024 * 700,
            "seeders": 100,
            "leechers": 10,
            "indexer": "Prowlarr",
            "publishDate": "2025-01-01T12:00:00Z",
        }
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert len(results) == 1
    assert results[0].title == "Test Torrent"
    assert results[0].seeders == 100
    assert results[0].source.name == "Prowlarr"
    assert isinstance(results[0].magnet_link, MagnetLink)
    assert isinstance(results[0].size, FileSize)


def test_indexer_source_adapter_skips_malformed_results() -> None:
    """Should skip malformed results and continue processing."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Valid Torrent",
            "size": 1024,
            "seeders": 50,
            "leechers": 5,
            "indexer": "Prowlarr",
        },
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "b" * 40,
            # Missing title - malformed
            "size": 2048,
            "seeders": 100,
            "leechers": 10,
            "indexer": "Prowlarr",
        },
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "c" * 40,
            "title": "Another Valid",
            "size": 3072,
            "seeders": 75,
            "leechers": 7,
            "indexer": "Prowlarr",
        },
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr", "Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    # Should have 2 valid results (skipped the malformed one)
    assert len(results) == 2
    assert results[0].title == "Valid Torrent"
    assert results[1].title == "Another Valid"


def test_indexer_source_adapter_handles_missing_magnet_url() -> None:
    """Should skip results missing both magnetUrl and guid."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Valid",
            "size": 1024,
            "seeders": 50,
            "leechers": 5,
            "indexer": "Prowlarr",
        },
        {
            "title": "No magnet link",
            "size": 2048,
            "seeders": 100,
            "leechers": 10,
            "indexer": "Prowlarr",
            # Missing both magnetUrl and guid
        },
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert len(results) == 1
    assert results[0].title == "Valid"


def test_indexer_source_adapter_uses_guid_fallback() -> None:
    """Should use guid if magnetUrl is missing."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "guid": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Test Torrent",
            "size": 1024,
            "seeders": 50,
            "leechers": 5,
            "indexer": "Prowlarr",
        }
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert len(results) == 1
    assert results[0].title == "Test Torrent"


def test_indexer_source_adapter_uses_peers_as_leechers_fallback() -> None:
    """Should use peers if leechers is missing."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Test Torrent",
            "size": 1024,
            "seeders": 50,
            "peers": 15,  # Use peers instead of leechers
            "indexer": "Prowlarr",
        }
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert len(results) == 1
    assert results[0].leechers == 15


def test_indexer_source_adapter_propagates_indexer_error() -> None:
    """Should propagate IndexerError from source."""
    mock_source = Mock()
    mock_source.search.side_effect = IndexerError("Search failed")

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)

    with pytest.raises(IndexerError):
        adapter.search(query="test")


def test_indexer_source_adapter_propagates_timeout_error() -> None:
    """Should propagate IndexerTimeoutError from source."""
    mock_source = Mock()
    mock_source.search.side_effect = IndexerTimeoutError("Timeout")

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)

    with pytest.raises(IndexerTimeoutError):
        adapter.search(query="test")


def test_indexer_source_adapter_get_available_indexers() -> None:
    """Should delegate to source's get_available_indexers."""
    mock_source = Mock()
    mock_source.get_available_indexers.return_value = ["Prowlarr", "Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    indexers = adapter.get_available_indexers()

    assert len(indexers) == 2
    assert "Prowlarr" in indexers
    assert "Prowlarr" in indexers
    mock_source.get_available_indexers.assert_called_once()


def test_indexer_source_adapter_forwards_search_parameters() -> None:
    """Should forward all parameters to source search method."""
    mock_source = Mock()
    mock_source.search.return_value = []
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    adapter.search(query="test query", indexer_names=["Prowlarr"], max_results=20)

    mock_source.search.assert_called_once_with(
        query="test query",
        indexer_names=["Prowlarr"],
        max_results=20,
    )


def test_indexer_source_adapter_maps_valid_iso_format_date() -> None:
    """Should correctly parse ISO format publish dates."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Test",
            "size": 1024,
            "seeders": 10,
            "leechers": 5,
            "indexer": "Prowlarr",
            "publishDate": "2025-06-15T14:30:45Z",
        }
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert len(results) == 1
    expected_date = datetime(2025, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
    assert results[0].date_found == expected_date


def test_indexer_source_adapter_handles_invalid_date_format() -> None:
    """Should use current date if publishDate format is invalid."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Test",
            "size": 1024,
            "seeders": 10,
            "leechers": 5,
            "indexer": "Prowlarr",
            "publishDate": "invalid-date-format",
        }
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert len(results) == 1
    # Should use current date, so just verify it's a datetime
    assert isinstance(results[0].date_found, datetime)


def test_indexer_source_adapter_handles_missing_publish_date() -> None:
    """Should use current date if publishDate is missing."""
    mock_source = Mock()
    mock_source.search.return_value = [
        {
            "magnetUrl": "magnet:?xt=urn:btih:" + "a" * 40,
            "title": "Test",
            "size": 1024,
            "seeders": 10,
            "leechers": 5,
            "indexer": "Prowlarr",
            # Missing publishDate
        }
    ]
    mock_source.get_available_indexers.return_value = ["Prowlarr"]

    adapter = ProwlarrIndexerManager(indexer_source=mock_source)
    results = adapter.search(query="test")

    assert len(results) == 1
    # Should use current date, so just verify it's a datetime
    assert isinstance(results[0].date_found, datetime)
