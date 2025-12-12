"""Tests for ProwlarrAdapter."""

from unittest.mock import Mock, patch

import pytest
import requests

from nodo.domain.exceptions import IndexerError, IndexerTimeoutError
from nodo.infrastructure.indexers import ProwlarrAdapter


def test_prowlarr_adapter_init() -> None:
    """Should initialize with base_url and api_key."""
    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")
    assert adapter._base_url == "http://localhost:9696"
    assert adapter._api_key == "test_key"


def test_prowlarr_adapter_init_strips_trailing_slash() -> None:
    """Should strip trailing slash from base_url."""
    adapter = ProwlarrAdapter(base_url="http://localhost:9696/", api_key="test_key")
    assert adapter._base_url == "http://localhost:9696"


def test_prowlarr_adapter_init_validates_empty_base_url() -> None:
    """Should raise ValueError for empty base_url."""
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        ProwlarrAdapter(base_url="", api_key="test_key")


def test_prowlarr_adapter_init_validates_empty_api_key() -> None:
    """Should raise ValueError for empty api_key."""
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        ProwlarrAdapter(base_url="http://localhost:9696", api_key="")


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_search_returns_raw_dictionaries(
    mock_session_class: Mock,
) -> None:
    """Should return raw result dictionaries from Prowlarr API."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    raw_data = [
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
    mock_response.json.return_value = raw_data
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")
    results = adapter.search(query="test")

    assert len(results) == 1
    assert results[0] == raw_data[0]
    assert results[0]["title"] == "Test Torrent"
    assert results[0]["seeders"] == 100


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_search_with_indexer_names(
    mock_session_class: Mock,
) -> None:
    """Should pass indexer_names parameter to search request."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")
    adapter.search(query="test", indexer_names=["Prowlarr"])

    call_args = mock_session.get.call_args
    assert "test" in str(call_args)


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_search_timeout(mock_session_class: Mock) -> None:
    """Should raise IndexerTimeoutError on timeout."""
    mock_session = Mock()
    mock_session.get.side_effect = requests.Timeout()
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")

    with pytest.raises(IndexerTimeoutError):
        adapter.search(query="test")


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_search_request_error(
    mock_session_class: Mock,
) -> None:
    """Should raise IndexerError on request failure."""
    mock_session = Mock()
    mock_session.get.side_effect = requests.RequestException("Network error")
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")

    with pytest.raises(IndexerError):
        adapter.search(query="test")


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_search_api_error(mock_session_class: Mock) -> None:
    """Should raise IndexerError on API error response."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")

    with pytest.raises(IndexerError, match="API error 500"):
        adapter.search(query="test")


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_search_non_list_response(
    mock_session_class: Mock,
) -> None:
    """Should raise IndexerError when response is not a list."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}  # Dict instead of list
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")

    with pytest.raises(IndexerError, match="Unexpected Prowlarr API response format"):
        adapter.search(query="test")


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_get_available_indexers(
    mock_session_class: Mock,
) -> None:
    """Should return list of available indexers."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "Prowlarr"},
        {"name": "Prowlarr"},
    ]
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")
    indexers = adapter.get_available_indexers()

    assert len(indexers) == 2
    assert "Prowlarr" in indexers
    assert "Prowlarr" in indexers


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_get_available_indexers_error(
    mock_session_class: Mock,
) -> None:
    """Should raise IndexerError on request failure."""
    mock_session = Mock()
    mock_session.get.side_effect = requests.RequestException("Network error")
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")

    with pytest.raises(IndexerError):
        adapter.get_available_indexers()


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_get_available_indexers_api_error(
    mock_session_class: Mock,
) -> None:
    """Should raise IndexerError on API error response."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")

    with pytest.raises(IndexerError, match="API error 500"):
        adapter.get_available_indexers()


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_get_available_indexers_non_list_response(
    mock_session_class: Mock,
) -> None:
    """Should raise IndexerError when indexers response is not a list."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"indexers": []}  # Dict instead of list
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")

    with pytest.raises(IndexerError, match="Unexpected Prowlarr API response format"):
        adapter.get_available_indexers()


@patch("nodo.infrastructure.indexers.prowlarr_adapter.requests.Session")
def test_prowlarr_adapter_get_available_indexers_skips_invalid_items(
    mock_session_class: Mock,
) -> None:
    """Should skip indexer items without 'name' field."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "Prowlarr"},
        {"title": "Invalid"},  # Missing 'name'
        {"name": "Prowlarr"},
        "invalid",  # Not a dict
        {"name": "RARBG"},
    ]
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    adapter = ProwlarrAdapter(base_url="http://localhost:9696", api_key="test_key")
    indexers = adapter.get_available_indexers()

    assert len(indexers) == 3
    assert "Prowlarr" in indexers
    assert "Prowlarr" in indexers
    assert "RARBG" in indexers


def test_prowlarr_adapter_init_validates_whitespace_base_url() -> None:
    """Should raise ValueError for whitespace-only base_url."""
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        ProwlarrAdapter(base_url="   ", api_key="test_key")


def test_prowlarr_adapter_init_validates_whitespace_api_key() -> None:
    """Should raise ValueError for whitespace-only api_key."""
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        ProwlarrAdapter(base_url="http://localhost:9696", api_key="   ")
