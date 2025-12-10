"""Tests for GetDownloadStatus use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest

from nodo.application.interfaces import (
    IDownloadRepository,
    ITorrentClient,
    TorrentStatus,
)
from nodo.application.use_cases.get_download_status import GetDownloadStatus
from nodo.domain.entities import Download
from nodo.domain.exceptions import (
    DownloadNotFoundError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import (
    AggregatorSource,
    DownloadStatus,
    FileSize,
    MagnetLink,
)


def test_get_download_status_success() -> None:
    """Should successfully get download status."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    torrent_hash = magnet_link.info_hash

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024 * 1024),
        status=DownloadStatus.DOWNLOADING,
    )

    torrent_status = TorrentStatus(
        progress=45.5,
        download_rate=1024 * 1024,  # 1 MB/s
        upload_rate=512 * 1024,  # 512 KB/s
        eta_seconds=3600,  # 1 hour
        is_complete=False,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.save.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    result = use_case.execute(input_data)

    assert result.download.id_ == str(download_id)
    assert result.progress == 45.5
    assert result.download_rate == "1.00 MB/s"
    assert result.upload_rate == "512.00 KB/s"
    assert result.eta == "1 hour"
    mock_repo.find_by_id.assert_called_once_with(download_id)
    mock_client.get_status.assert_called_once_with(torrent_hash)


def test_get_download_status_raises_error_for_invalid_uuid() -> None:
    """Should raise ValidationError for invalid UUID format."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_client = Mock(spec=ITorrentClient)

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id="invalid-uuid")

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "Invalid download ID format" in str(exc_info.value)
    mock_repo.find_by_id.assert_not_called()
    mock_client.get_status.assert_not_called()


def test_get_download_status_raises_error_when_not_found() -> None:
    """Should raise DownloadNotFoundError when download not found."""
    download_id = uuid4()

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = None

    mock_client = Mock(spec=ITorrentClient)

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    with pytest.raises(DownloadNotFoundError) as exc_info:
        use_case.execute(input_data)

    assert str(download_id) in str(exc_info.value)
    mock_repo.find_by_id.assert_called_once_with(download_id)
    mock_client.get_status.assert_not_called()


def test_get_download_status_raises_error_for_torrent_client_failure() -> None:
    """Should raise TorrentClientError when client fails."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    torrent_hash = magnet_link.info_hash

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.side_effect = TorrentClientError("Client connection failed")

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    with pytest.raises(TorrentClientError) as exc_info:
        use_case.execute(input_data)

    assert "Failed to get status from torrent client" in str(exc_info.value)
    mock_client.get_status.assert_called_once_with(torrent_hash)


def test_get_download_status_handles_torrent_not_in_client() -> None:
    """Should handle case when torrent is not found in client."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadStatus.DOWNLOADING,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = None  # Torrent not found in client

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    result = use_case.execute(input_data)

    assert result.download.id_ == str(download_id)
    assert result.progress == 0.0
    assert result.download_rate is None
    assert result.upload_rate is None
    assert result.eta is None
    # Should not save when torrent not found
    mock_repo.save.assert_not_called()


def test_get_download_status_updates_to_completed() -> None:
    """Should update download status to COMPLETED when torrent completes."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadStatus.DOWNLOADING,
    )

    torrent_status = TorrentStatus(
        progress=100.0,
        download_rate=0,
        upload_rate=1024 * 1024,
        eta_seconds=None,
        is_complete=True,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.save.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    result = use_case.execute(input_data)

    assert result.download.status == "COMPLETED"
    # Verify download was updated and saved
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.status == DownloadStatus.COMPLETED
    assert saved_download.date_completed is not None
    mock_repo.save.assert_called_once()


def test_get_download_status_updates_to_paused() -> None:
    """Should update download status to PAUSED when torrent is paused."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadStatus.DOWNLOADING,
    )

    torrent_status = TorrentStatus(
        progress=50.0,
        download_rate=0,
        upload_rate=0,
        eta_seconds=1800,
        is_complete=False,
        is_paused=True,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.save.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    result = use_case.execute(input_data)

    assert result.download.status == "PAUSED"
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.status == DownloadStatus.PAUSED
    mock_repo.save.assert_called_once()


def test_get_download_status_updates_from_paused_to_downloading() -> None:
    """Should update download status from PAUSED to DOWNLOADING when resumed."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadStatus.PAUSED,
    )

    torrent_status = TorrentStatus(
        progress=50.0,
        download_rate=1024 * 1024,
        upload_rate=512 * 1024,
        eta_seconds=1800,
        is_complete=False,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.save.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    result = use_case.execute(input_data)

    assert result.download.status == "DOWNLOADING"
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.status == DownloadStatus.DOWNLOADING
    mock_repo.save.assert_called_once()


def test_get_download_status_does_not_update_when_status_unchanged() -> None:
    """Should not update download if status hasn't changed."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadStatus.DOWNLOADING,
    )

    torrent_status = TorrentStatus(
        progress=50.0,
        download_rate=1024 * 1024,
        upload_rate=512 * 1024,
        eta_seconds=1800,
        is_complete=False,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.save.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = GetDownloadStatus(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = GetDownloadStatus.Input(download_id=str(download_id))

    result = use_case.execute(input_data)

    assert result.download.status == "DOWNLOADING"
    # Should still save (in case progress changed, even if status didn't)
    mock_repo.save.assert_called_once()


def test_format_speed_zero_bytes() -> None:
    """Should format zero bytes per second correctly."""
    assert GetDownloadStatus._format_speed(0) == "0 B/s"


def test_format_speed_bytes() -> None:
    """Should format bytes per second correctly."""
    assert GetDownloadStatus._format_speed(512) == "512 B/s"


def test_format_speed_kilobytes() -> None:
    """Should format kilobytes per second correctly."""
    assert GetDownloadStatus._format_speed(1024) == "1.00 KB/s"


def test_format_speed_megabytes() -> None:
    """Should format megabytes per second correctly."""
    assert GetDownloadStatus._format_speed(1024 * 1024) == "1.00 MB/s"


def test_format_speed_gigabytes() -> None:
    """Should format gigabytes per second correctly."""
    assert GetDownloadStatus._format_speed(1024 * 1024 * 1024) == "1.00 GB/s"


def test_format_speed_negative_returns_none() -> None:
    """Should return None for negative speed values."""
    assert GetDownloadStatus._format_speed(-1) is None


def test_format_speed_too_large_returns_none() -> None:
    """Should return None for unreasonably large speed values."""
    # Max reasonable is 1 PB/s (1024^5)
    max_reasonable = 1024**5
    assert GetDownloadStatus._format_speed(max_reasonable + 1) is None


def test_format_speed_handles_filesize_validation_error() -> None:
    """Should return None if FileSize validation fails."""
    from unittest.mock import patch

    with patch(
        "nodo.application.use_cases.get_download_status.FileSize"
    ) as mock_filesize:
        mock_filesize.from_bytes.side_effect = ValidationError("Invalid size")
        # Use a valid value that would normally work
        result = GetDownloadStatus._format_speed(1024)
        assert result is None


def test_format_eta_unknown() -> None:
    """Should format unknown ETA correctly."""
    assert GetDownloadStatus._format_eta(None) is None
    assert GetDownloadStatus._format_eta(-1) is None


def test_format_eta_seconds() -> None:
    """Should format ETA in seconds correctly."""
    assert GetDownloadStatus._format_eta(0) == "0 seconds"
    assert GetDownloadStatus._format_eta(1) == "1 second"
    assert GetDownloadStatus._format_eta(30) == "30 seconds"
    assert GetDownloadStatus._format_eta(59) == "59 seconds"


def test_format_eta_minutes() -> None:
    """Should format ETA in minutes correctly."""
    assert GetDownloadStatus._format_eta(60) == "1 minute"
    assert GetDownloadStatus._format_eta(120) == "2 minutes"
    assert GetDownloadStatus._format_eta(3599) == "59 minutes"


def test_format_eta_hours() -> None:
    """Should format ETA in hours correctly."""
    assert GetDownloadStatus._format_eta(3600) == "1 hour"
    assert GetDownloadStatus._format_eta(7200) == "2 hours"
    assert GetDownloadStatus._format_eta(3660) == "1 hour 1 minute"
    assert GetDownloadStatus._format_eta(3720) == "1 hour 2 minutes"


def test_format_eta_days() -> None:
    """Should format ETA in days correctly."""
    assert GetDownloadStatus._format_eta(86400) == "1 day"
    assert GetDownloadStatus._format_eta(172800) == "2 days"
    assert GetDownloadStatus._format_eta(90000) == "1 day 1 hour"
    assert GetDownloadStatus._format_eta(90060) == "1 day 1 hour 1 minute"
    # Test days with minutes but no hours
    assert GetDownloadStatus._format_eta(86460) == "1 day 1 minute"
    assert GetDownloadStatus._format_eta(86520) == "1 day 2 minutes"


def test_format_eta_too_large_returns_none() -> None:
    """Should return None for unreasonably large ETA values."""
    # Max reasonable is 100 years in seconds
    max_reasonable = 100 * 365 * 24 * 60 * 60
    assert GetDownloadStatus._format_eta(max_reasonable + 1) is None


def test_to_dto_converts_correctly() -> None:
    """Should convert Download entity to DTO correctly."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    date_added = datetime(2025, 1, 1, 12, 0, 0)
    date_completed = datetime(2025, 1, 1, 13, 0, 0)

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadStatus.COMPLETED,
        date_added=date_added,
        date_completed=date_completed,
    )

    dto = GetDownloadStatus._to_dto(download)

    assert dto.id_ == str(download_id)
    assert dto.magnet_link == str(magnet_link)
    assert dto.title == "Test Download"
    assert dto.file_path == "/downloads/test"
    assert dto.source == "1337x"
    assert dto.status == "COMPLETED"
    assert dto.date_added == date_added
    assert dto.date_completed == date_completed
    assert dto.size == "1.00 MB"
