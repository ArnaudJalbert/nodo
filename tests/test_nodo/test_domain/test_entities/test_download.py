"""Tests for Download entity."""

from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from nodo.domain.entities import Download
from nodo.domain.value_objects import (
    AggregatorSource,
    DownloadState,
    FileSize,
    MagnetLink,
)


def test_download_create_with_required_fields() -> None:
    """Should create Download with required fields and defaults."""
    magnet = MagnetLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    size = FileSize(bytes_=1024 * 1024 * 700)
    source = AggregatorSource(name="1337x")
    file_path = Path("/downloads/ubuntu.iso")

    download = Download(
        magnet_link=magnet,
        title="Ubuntu 24.04 LTS",
        file_path=file_path,
        source=source,
        size=size,
    )

    assert download.magnet_link == magnet
    assert download.title == "Ubuntu 24.04 LTS"
    assert download.file_path == file_path
    assert download.source == source
    assert download.size == size
    assert download.status == DownloadState.DOWNLOADING
    assert download.date_completed is None
    assert isinstance(download.id_, UUID)
    assert isinstance(download.date_added, datetime)


def test_download_create_with_all_fields() -> None:
    """Should create Download with all fields specified."""
    magnet = MagnetLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    size = FileSize(bytes_=1024 * 1024 * 700)
    source = AggregatorSource(name="1337x")
    file_path = Path("/downloads/ubuntu.iso")
    custom_id = uuid4()
    date_added = datetime(2025, 1, 15, 10, 0, 0)
    date_completed = datetime(2025, 1, 15, 11, 0, 0)

    download = Download(
        magnet_link=magnet,
        title="Ubuntu 24.04 LTS",
        file_path=file_path,
        source=source,
        size=size,
        id_=custom_id,
        status=DownloadState.COMPLETED,
        date_added=date_added,
        date_completed=date_completed,
    )

    assert download.id_ == custom_id
    assert download.status == DownloadState.COMPLETED
    assert download.date_added == date_added
    assert download.date_completed == date_completed


def test_download_status_is_mutable() -> None:
    """Download status should be mutable."""
    download = Download(
        magnet_link=MagnetLink(
            uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
        ),
        title="Test",
        file_path=Path("/downloads/test"),
        source=AggregatorSource(name="1337x"),
        size=FileSize(bytes_=1024),
    )

    assert download.status == DownloadState.DOWNLOADING
    download.status = DownloadState.COMPLETED
    assert download.status == DownloadState.COMPLETED


def test_download_date_completed_is_mutable() -> None:
    """Download date_completed should be mutable."""
    download = Download(
        magnet_link=MagnetLink(
            uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
        ),
        title="Test",
        file_path=Path("/downloads/test"),
        source=AggregatorSource(name="1337x"),
        size=FileSize(bytes_=1024),
    )

    assert download.date_completed is None
    completed_time = datetime.now()
    download.date_completed = completed_time
    assert download.date_completed == completed_time


def test_download_requires_keyword_arguments() -> None:
    """Download should require keyword arguments."""
    with pytest.raises(TypeError):
        Download(  # type: ignore[misc]
            MagnetLink(
                uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
            ),
            "Test",
            Path("/downloads/test"),
            AggregatorSource(name="1337x"),
            FileSize(bytes_=1024),
        )


def test_download_each_instance_gets_unique_id() -> None:
    """Each Download instance should get a unique ID by default."""
    download1 = Download(
        magnet_link=MagnetLink(
            uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
        ),
        title="Test 1",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource(name="1337x"),
        size=FileSize(bytes_=1024),
    )
    download2 = Download(
        magnet_link=MagnetLink(
            uri="magnet:?xt=urn:btih:abcdef1234567890abcdef1234567890abcdef12"
        ),
        title="Test 2",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource(name="1337x"),
        size=FileSize(bytes_=2048),
    )

    assert download1.id_ != download2.id_
