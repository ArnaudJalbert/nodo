"""Tests for PauseDownload use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import IDownloadRepository, ITorrentClient
from nodo.application.use_cases.pause_download import PauseDownload
from nodo.domain.entities import Download
from nodo.domain.exceptions import (
    DownloadNotFoundError,
    InvalidStateTransitionError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import (
    DownloadState,
    FileSize,
    IndexerSource,
    MagnetLink,
)


def test_pause_download_success() -> None:
    """Should successfully pause a downloading download."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    torrent_hash = magnet_link.info_hash

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.save.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_client.pause.return_value = True

    use_case = PauseDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = PauseDownload.Input(download_id=str(download_id))
    result = use_case.execute(input_data)

    assert isinstance(result.download, DownloadDTO)
    assert result.download.status == "PAUSED"
    mock_repo.find_by_id.assert_called_once_with(download_id)
    mock_client.pause.assert_called_once_with(torrent_hash)
    mock_repo.save.assert_called_once()
    # Verify the saved download has PAUSED status
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.status == DownloadState.PAUSED


def test_pause_download_raises_error_for_invalid_uuid() -> None:
    """Should raise ValidationError for invalid UUID format."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_client = Mock(spec=ITorrentClient)

    use_case = PauseDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = PauseDownload.Input(download_id="invalid-uuid")

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "invalid download id format" in str(exc_info.value).lower()
    mock_repo.find_by_id.assert_not_called()
    mock_client.pause.assert_not_called()


def test_pause_download_raises_error_for_not_found() -> None:
    """Should raise DownloadNotFoundError when download not found."""
    download_id = uuid4()

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = None

    mock_client = Mock(spec=ITorrentClient)

    use_case = PauseDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = PauseDownload.Input(download_id=str(download_id))

    with pytest.raises(DownloadNotFoundError) as exc_info:
        use_case.execute(input_data)

    assert "not found" in str(exc_info.value).lower()
    mock_client.pause.assert_not_called()
    mock_repo.save.assert_not_called()


def test_pause_download_raises_error_for_invalid_status() -> None:
    """Should raise InvalidStateTransitionError for non-DOWNLOADING status."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.PAUSED,  # Already paused
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download

    mock_client = Mock(spec=ITorrentClient)

    use_case = PauseDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = PauseDownload.Input(download_id=str(download_id))

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        use_case.execute(input_data)

    assert "cannot pause" in str(exc_info.value).lower()
    assert "downloading" in str(exc_info.value).lower()
    mock_client.pause.assert_not_called()
    mock_repo.save.assert_not_called()


def test_pause_download_raises_error_for_completed_status() -> None:
    """Should raise InvalidStateTransitionError for COMPLETED status."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.COMPLETED,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download

    mock_client = Mock(spec=ITorrentClient)

    use_case = PauseDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = PauseDownload.Input(download_id=str(download_id))

    with pytest.raises(InvalidStateTransitionError):
        use_case.execute(input_data)

    mock_client.pause.assert_not_called()
    mock_repo.save.assert_not_called()


def test_pause_download_raises_error_for_torrent_client_failure() -> None:
    """Should raise TorrentClientError when client pause fails."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download

    mock_client = Mock(spec=ITorrentClient)
    mock_client.pause.side_effect = TorrentClientError("Client error")

    use_case = PauseDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = PauseDownload.Input(download_id=str(download_id))

    with pytest.raises(TorrentClientError) as exc_info:
        use_case.execute(input_data)

    assert "torrent client" in str(exc_info.value).lower()
    mock_repo.save.assert_not_called()


def test_pause_download_raises_error_when_torrent_not_found_in_client() -> None:
    """Should raise TorrentClientError when torrent not found in client."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download

    mock_client = Mock(spec=ITorrentClient)
    mock_client.pause.return_value = False  # Not found in client

    use_case = PauseDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = PauseDownload.Input(download_id=str(download_id))

    with pytest.raises(TorrentClientError) as exc_info:
        use_case.execute(input_data)

    assert "not found in client" in str(exc_info.value).lower()
    mock_repo.save.assert_not_called()


def test_to_dto_converts_correctly() -> None:
    """Should convert Download entity to DTO correctly."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    file_path = Path("/downloads/test")
    source = IndexerSource.from_string("Prowlarr")
    size = FileSize.from_bytes(1024 * 1024)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=file_path,
        source=source,
        size=size,
        status=DownloadState.PAUSED,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    dto = PauseDownload._to_dto(download)

    assert dto.id_ == str(download_id)
    assert dto.magnet_link == str(magnet_link)
    assert dto.title == "Test Download"
    assert dto.file_path == str(file_path)
    assert dto.source == str(source)
    assert dto.size == str(size)
    assert dto.status == "PAUSED"
    assert dto.date_added == datetime(2025, 1, 1, 12, 0, 0)
