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


def test_torrent_search_result_equality_by_magnet_link_only() -> None:
    """
    TorrentSearchResults with same magnet link should
    be equal even if other fields differ.
    """
    magnet = MagnetLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )

    result1 = TorrentSearchResult(
        magnet_link=magnet,
        title="Title 1",
        size=FileSize(bytes_=1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource(name="1337x"),
        date_found=datetime(2025, 1, 15),
    )
    result2 = TorrentSearchResult(
        magnet_link=magnet,
        title="Title 2",  # Different title
        size=FileSize(bytes_=2048),  # Different size
        seeders=100,  # Different seeders
        leechers=10,  # Different leechers
        source=AggregatorSource(name="ThePirateBay"),  # Different source
        date_found=datetime(2025, 1, 16),  # Different date
    )

    # Should be equal because they have the same magnet link
    assert result1 == result2
    assert hash(result1) == hash(result2)


def test_torrent_search_result_hashable() -> None:
    """TorrentSearchResult should be hashable and usable in sets."""
    magnet1 = MagnetLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    magnet2 = MagnetLink(
        uri="magnet:?xt=urn:btih:abcdef1234567890abcdef1234567890abcdef12"
    )

    result1 = TorrentSearchResult(
        magnet_link=magnet1,
        title="Result 1",
        size=FileSize(bytes_=1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource(name="1337x"),
        date_found=datetime(2025, 1, 15),
    )
    result2 = TorrentSearchResult(
        magnet_link=magnet2,
        title="Result 2",
        size=FileSize(bytes_=2048),
        seeders=100,
        leechers=10,
        source=AggregatorSource(name="ThePirateBay"),
        date_found=datetime(2025, 1, 16),
    )
    result3 = TorrentSearchResult(
        magnet_link=magnet1,  # Same as result1
        title="Result 3",  # Different title
        size=FileSize(bytes_=4096),  # Different size
        seeders=200,  # Different seeders
        leechers=20,  # Different leechers
        source=AggregatorSource(name="RARBG"),  # Different source
        date_found=datetime(2025, 1, 17),  # Different date
    )

    # Create a set - should deduplicate by magnet link
    result_set = {result1, result2, result3}

    # Should only have 2 items (result1 and result3 have same magnet link)
    assert len(result_set) == 2
    assert result1 in result_set
    assert result2 in result_set
    assert result3 in result_set  # Should be in set but equal to result1


def test_torrent_search_result_equality_with_different_type() -> None:
    """
    TorrentSearchResult equality should return False when
    comparing with different types.
    """
    result = TorrentSearchResult(
        magnet_link=MagnetLink(
            uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
        ),
        title="Test",
        size=FileSize(bytes_=1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource(name="1337x"),
        date_found=datetime(2025, 1, 15),
    )

    # Comparing with a different type should return False
    # (Python converts NotImplemented to False)
    assert (result == "not a TorrentSearchResult") is False
