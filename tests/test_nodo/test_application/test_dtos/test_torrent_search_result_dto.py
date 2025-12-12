"""Tests for TorrentSearchResultDTO."""

from datetime import datetime

import pytest

from nodo.application.dtos import TorrentSearchResultDTO


def test_torrent_search_result_dto_create_with_all_fields() -> None:
    """Should create TorrentSearchResultDTO with all fields."""
    date_found = datetime(2025, 1, 1, 12, 0, 0)

    dto = TorrentSearchResultDTO(
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        size="1.40 GB",
        seeders=150,
        leechers=25,
        source="Prowlarr",
        date_found=date_found,
    )

    assert (
        dto.magnet_link
        == "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    assert dto.title == "Ubuntu 24.04 LTS"
    assert dto.size == "1.40 GB"
    assert dto.seeders == 150
    assert dto.leechers == 25
    assert dto.source == "Prowlarr"
    assert dto.date_found == date_found


def test_torrent_search_result_dto_with_zero_seeders() -> None:
    """Should create TorrentSearchResultDTO with zero seeders."""
    date_found = datetime(2025, 1, 1, 12, 0, 0)

    dto = TorrentSearchResultDTO(
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Test Torrent",
        size="500 MB",
        seeders=0,
        leechers=10,
        source="ThePirateBay",
        date_found=date_found,
    )

    assert dto.seeders == 0
    assert dto.leechers == 10


def test_torrent_search_result_dto_is_frozen() -> None:
    """Should be immutable (frozen dataclass)."""
    date_found = datetime(2025, 1, 1, 12, 0, 0)

    dto = TorrentSearchResultDTO(
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        size="1.40 GB",
        seeders=150,
        leechers=25,
        source="Prowlarr",
        date_found=date_found,
    )

    with pytest.raises(Exception):  # noqa: B017, PT011
        dto.title = "Modified"  # type: ignore[misc]


def test_torrent_search_result_dto_equality() -> None:
    """Should compare DTOs by value."""
    date_found = datetime(2025, 1, 1, 12, 0, 0)

    dto1 = TorrentSearchResultDTO(
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        size="1.40 GB",
        seeders=150,
        leechers=25,
        source="Prowlarr",
        date_found=date_found,
    )

    dto2 = TorrentSearchResultDTO(
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        size="1.40 GB",
        seeders=150,
        leechers=25,
        source="Prowlarr",
        date_found=date_found,
    )

    assert dto1 == dto2
    assert hash(dto1) == hash(dto2)


def test_torrent_search_result_dto_different_values_not_equal() -> None:
    """Should not be equal when values differ."""
    date_found = datetime(2025, 1, 1, 12, 0, 0)

    dto1 = TorrentSearchResultDTO(
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        size="1.40 GB",
        seeders=150,
        leechers=25,
        source="Prowlarr",
        date_found=date_found,
    )

    dto2 = TorrentSearchResultDTO(
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Different Title",
        size="1.40 GB",
        seeders=150,
        leechers=25,
        source="Prowlarr",
        date_found=date_found,
    )

    assert dto1 != dto2
