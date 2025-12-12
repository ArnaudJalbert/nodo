"""Tests for DownloadDTO."""

from datetime import datetime

import pytest

from nodo.application.dtos import DownloadDTO


def test_download_dto_create_with_all_fields() -> None:
    """Should create DownloadDTO with all fields."""
    date_added = datetime(2025, 1, 1, 12, 0, 0)
    date_completed = datetime(2025, 1, 1, 13, 0, 0)

    dto = DownloadDTO(
        id_="123e4567-e89b-12d3-a456-426614174000",
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        file_path="/downloads/ubuntu.iso",
        source="Prowlarr",
        status="DOWNLOADING",
        date_added=date_added,
        date_completed=date_completed,
        size="1.40 GB",
    )

    assert dto.id_ == "123e4567-e89b-12d3-a456-426614174000"
    assert (
        dto.magnet_link
        == "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    assert dto.title == "Ubuntu 24.04 LTS"
    assert dto.file_path == "/downloads/ubuntu.iso"
    assert dto.source == "Prowlarr"
    assert dto.status == "DOWNLOADING"
    assert dto.date_added == date_added
    assert dto.date_completed == date_completed
    assert dto.size == "1.40 GB"


def test_download_dto_create_without_date_completed() -> None:
    """Should create DownloadDTO without date_completed."""
    date_added = datetime(2025, 1, 1, 12, 0, 0)

    dto = DownloadDTO(
        id_="123e4567-e89b-12d3-a456-426614174000",
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        file_path="/downloads/ubuntu.iso",
        source="Prowlarr",
        status="DOWNLOADING",
        date_added=date_added,
        date_completed=None,
        size="1.40 GB",
    )

    assert dto.date_completed is None


def test_download_dto_is_frozen() -> None:
    """Should be immutable (frozen dataclass)."""
    date_added = datetime(2025, 1, 1, 12, 0, 0)

    dto = DownloadDTO(
        id_="123e4567-e89b-12d3-a456-426614174000",
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        file_path="/downloads/ubuntu.iso",
        source="Prowlarr",
        status="DOWNLOADING",
        date_added=date_added,
        date_completed=None,
        size="1.40 GB",
    )

    with pytest.raises(Exception):  # noqa: B017, PT011
        dto.title = "Modified"  # type: ignore[misc]


def test_download_dto_equality() -> None:
    """Should compare DTOs by value."""
    date_added = datetime(2025, 1, 1, 12, 0, 0)

    dto1 = DownloadDTO(
        id_="123e4567-e89b-12d3-a456-426614174000",
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        file_path="/downloads/ubuntu.iso",
        source="Prowlarr",
        status="DOWNLOADING",
        date_added=date_added,
        date_completed=None,
        size="1.40 GB",
    )

    dto2 = DownloadDTO(
        id_="123e4567-e89b-12d3-a456-426614174000",
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        file_path="/downloads/ubuntu.iso",
        source="Prowlarr",
        status="DOWNLOADING",
        date_added=date_added,
        date_completed=None,
        size="1.40 GB",
    )

    assert dto1 == dto2
    assert hash(dto1) == hash(dto2)


def test_download_dto_different_values_not_equal() -> None:
    """Should not be equal when values differ."""
    date_added = datetime(2025, 1, 1, 12, 0, 0)

    dto1 = DownloadDTO(
        id_="123e4567-e89b-12d3-a456-426614174000",
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Ubuntu 24.04 LTS",
        file_path="/downloads/ubuntu.iso",
        source="Prowlarr",
        status="DOWNLOADING",
        date_added=date_added,
        date_completed=None,
        size="1.40 GB",
    )

    dto2 = DownloadDTO(
        id_="123e4567-e89b-12d3-a456-426614174000",
        magnet_link="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678",
        title="Different Title",
        file_path="/downloads/ubuntu.iso",
        source="Prowlarr",
        status="DOWNLOADING",
        date_added=date_added,
        date_completed=None,
        size="1.40 GB",
    )

    assert dto1 != dto2
