"""Tests for TorrentSearchResult entity."""

from datetime import datetime

import pytest

from nodo.domain.entities import TorrentSearchResult
from nodo.domain.value_objects import AggregatorSource, FileSize, MagnetLink


def test_torrent_search_result_create_with_all_fields() -> None:
    """Should create TorrentSearchResult with all required fields."""
    magnet = MagnetLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    size = FileSize(bytes_=1024 * 1024 * 700)
    source = AggregatorSource(name="1337x")
    date_found = datetime(2025, 1, 15, 10, 30, 0)

    result = TorrentSearchResult(
        magnet_link=magnet,
        title="Ubuntu 24.04 LTS",
        size=size,
        seeders=100,
        leechers=10,
        source=source,
        date_found=date_found,
    )

    assert result.magnet_link == magnet
    assert result.title == "Ubuntu 24.04 LTS"
    assert result.size == size
    assert result.seeders == 100
    assert result.leechers == 10
    assert result.source == source
    assert result.date_found == date_found


def test_torrent_search_result_is_immutable() -> None:
    """TorrentSearchResult should be immutable (frozen)."""
    result = TorrentSearchResult(
        magnet_link=MagnetLink(
            uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
        ),
        title="Test Torrent",
        size=FileSize(bytes_=1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource(name="1337x"),
        date_found=datetime.now(),
    )

    with pytest.raises(AttributeError):
        result.title = "New Title"  # type: ignore[misc]


def test_torrent_search_result_requires_keyword_arguments() -> None:
    """TorrentSearchResult should require keyword arguments."""
    with pytest.raises(TypeError):
        TorrentSearchResult(  # type: ignore[misc]
            MagnetLink(
                uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
            ),
            "Test",
            FileSize(bytes_=1024),
            50,
            5,
            AggregatorSource(name="1337x"),
            datetime.now(),
        )


def test_torrent_search_result_equality() -> None:
    """TorrentSearchResults with same values should be equal."""
    magnet = MagnetLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    size = FileSize(bytes_=1024)
    source = AggregatorSource(name="1337x")
    date = datetime(2025, 1, 15)

    result1 = TorrentSearchResult(
        magnet_link=magnet,
        title="Test",
        size=size,
        seeders=50,
        leechers=5,
        source=source,
        date_found=date,
    )
    result2 = TorrentSearchResult(
        magnet_link=magnet,
        title="Test",
        size=size,
        seeders=50,
        leechers=5,
        source=source,
        date_found=date,
    )

    assert result1 == result2
