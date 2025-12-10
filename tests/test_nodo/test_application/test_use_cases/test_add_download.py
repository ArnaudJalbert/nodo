"""Tests for AddDownload use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import IDownloadRepository, ITorrentClient
from nodo.application.use_cases.add_download import AddDownload
from nodo.domain.entities import Download
from nodo.domain.exceptions import (
    DuplicateDownloadError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import AggregatorSource, FileSize, MagnetLink


def test_add_download_success() -> None:
    """Should successfully add a download."""
    magnet_link_str = "magnet:?xt=urn:btih:" + "a" * 40
    title = "Test Download"
    source = "1337x"
    size = "1.5 GB"
    file_path = "/downloads/test_download"

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists_by_magnet_link.return_value = False
    mock_repo.save.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_client.add_torrent.return_value = "torrent_hash_123"

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link=magnet_link_str,
        title=title,
        source=source,
        size=size,
        file_path=file_path,
    )

    result = use_case.execute(input_data)

    assert isinstance(result.download, DownloadDTO)
    assert result.download.magnet_link == magnet_link_str
    assert result.download.title == title
    assert result.download.source == source
    assert result.download.file_path == file_path
    assert result.download.status == "DOWNLOADING"
    mock_repo.exists_by_magnet_link.assert_called_once()
    mock_repo.save.assert_called_once()
    mock_client.add_torrent.assert_called_once()


def test_add_download_uses_provided_file_path() -> None:
    """Should use provided file path."""
    magnet_link_str = "magnet:?xt=urn:btih:" + "a" * 40
    file_path = "/custom/path/download"

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists_by_magnet_link.return_value = False

    mock_client = Mock(spec=ITorrentClient)
    mock_client.add_torrent.return_value = "torrent_hash_123"

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link=magnet_link_str,
        title="Test",
        source="1337x",
        size="1 GB",
        file_path=file_path,
    )

    result = use_case.execute(input_data)

    assert result.download.file_path == file_path
    # Verify directory from file_path was used in torrent client call
    call_args = mock_client.add_torrent.call_args
    assert "/custom/path" in str(call_args[0][1])


def test_add_download_raises_error_for_duplicate() -> None:
    """Should raise DuplicateDownloadError for duplicate magnet link."""
    magnet_link_str = "magnet:?xt=urn:btih:" + "a" * 40

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists_by_magnet_link.return_value = True

    mock_client = Mock(spec=ITorrentClient)

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link=magnet_link_str,
        title="Test",
        source="1337x",
        size="1 GB",
        file_path="/downloads/test",
    )

    with pytest.raises(DuplicateDownloadError) as exc_info:
        use_case.execute(input_data)

    assert "already exists" in str(exc_info.value).lower()
    mock_repo.save.assert_not_called()
    mock_client.add_torrent.assert_not_called()


def test_add_download_raises_error_for_empty_title() -> None:
    """Should raise ValidationError for empty title."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_client = Mock(spec=ITorrentClient)

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link="magnet:?xt=urn:btih:" + "a" * 40,
        title="",
        source="1337x",
        size="1 GB",
        file_path="/downloads/test",
    )

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "title" in str(exc_info.value).lower()
    assert "empty" in str(exc_info.value).lower()


def test_add_download_raises_error_for_invalid_magnet_link() -> None:
    """Should raise ValidationError for invalid magnet link."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_client = Mock(spec=ITorrentClient)

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link="invalid_magnet_link",
        title="Test",
        source="1337x",
        size="1 GB",
        file_path="/downloads/test",
    )

    with pytest.raises(ValidationError):
        use_case.execute(input_data)


def test_add_download_raises_error_for_invalid_size() -> None:
    """Should raise ValidationError for invalid size format."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists_by_magnet_link.return_value = False

    mock_client = Mock(spec=ITorrentClient)

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link="magnet:?xt=urn:btih:" + "a" * 40,
        title="Test",
        source="1337x",
        size="invalid_size",
        file_path="/downloads/test",
    )

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert (
        "size" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()
    )


def test_add_download_raises_error_for_invalid_source() -> None:
    """Should raise ValidationError for invalid aggregator source."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists_by_magnet_link.return_value = False

    mock_client = Mock(spec=ITorrentClient)

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link="magnet:?xt=urn:btih:" + "a" * 40,
        title="Test",
        source="",
        size="1 GB",
        file_path="/downloads/test",
    )

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert (
        "aggregator" in str(exc_info.value).lower()
        or "source" in str(exc_info.value).lower()
    )


def test_add_download_raises_error_for_torrent_client_failure() -> None:
    """Should raise TorrentClientError when client fails."""
    magnet_link_str = "magnet:?xt=urn:btih:" + "a" * 40

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.exists_by_magnet_link.return_value = False

    mock_client = Mock(spec=ITorrentClient)
    mock_client.add_torrent.side_effect = TorrentClientError("Client error")

    use_case = AddDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = AddDownload.Input(
        magnet_link=magnet_link_str,
        title="Test",
        source="1337x",
        size="1 GB",
        file_path="/downloads/test",
    )

    with pytest.raises(TorrentClientError) as exc_info:
        use_case.execute(input_data)

    assert "torrent client" in str(exc_info.value).lower()
    # Repository save should still be called (download entity created)
    mock_repo.save.assert_called_once()


def test_to_dto_converts_correctly() -> None:
    """Should convert Download entity to DTO correctly."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    file_path = Path("/downloads/test")
    source = AggregatorSource.from_string("1337x")
    size = FileSize.from_bytes(1024 * 1024)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=file_path,
        source=source,
        size=size,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    dto = AddDownload._to_dto(download)

    assert dto.id_ == str(download_id)
    assert dto.magnet_link == str(magnet_link)
    assert dto.title == "Test Download"
    assert dto.file_path == str(file_path)
    assert dto.source == str(source)
    assert dto.size == str(size)
    assert dto.status == "DOWNLOADING"
    assert dto.date_added == datetime(2025, 1, 1, 12, 0, 0)
