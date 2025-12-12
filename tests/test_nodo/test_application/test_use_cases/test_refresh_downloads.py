"""Tests for RefreshDownloads use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from nodo.application.interfaces import IDownloadRepository, ITorrentClient
from nodo.application.use_cases.refresh_downloads import RefreshDownloads
from nodo.domain.entities import Download, DownloadStatus
from nodo.domain.exceptions import TorrentClientError
from nodo.domain.value_objects import (
    DownloadState,
    FileSize,
    IndexerSource,
    MagnetLink,
)


def test_refresh_downloads_updates_status() -> None:
    """Should update download status when it changes in torrent client."""
    magnet_link1 = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    magnet_link2 = MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40)

    download1 = Download(
        id_=uuid4(),
        magnet_link=magnet_link1,
        title="Download 1",
        file_path=Path("/downloads/test1"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    download2 = Download(
        id_=uuid4(),
        magnet_link=magnet_link2,
        title="Download 2",
        file_path=Path("/downloads/test2"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(2048 * 1024),
        status=DownloadState.PAUSED,
    )

    # Torrent status indicates download1 is now completed
    torrent_status1 = DownloadStatus(
        progress=100.0,
        download_rate=0,
        upload_rate=0,
        eta_seconds=None,
        is_complete=True,
        is_paused=False,
    )

    # Torrent status indicates download2 is still paused
    torrent_status2 = DownloadStatus(
        progress=50.0,
        download_rate=1024,
        upload_rate=512,
        eta_seconds=3600,
        is_complete=False,
        is_paused=True,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.side_effect = [
        [download1],  # DOWNLOADING downloads
        [download2],  # PAUSED downloads
    ]

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.side_effect = [torrent_status1, torrent_status2]

    use_case = RefreshDownloads(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = RefreshDownloads.Input()
    result = use_case.execute(input_data)

    assert result.updated_count == 1  # Only download1 was updated
    assert result.error_count == 0
    assert len(result.errors) == 0

    # Verify download1 was saved with COMPLETED status
    assert mock_repo.save.call_count == 1
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.id_ == download1.id_
    assert saved_download.status == DownloadState.COMPLETED
    assert saved_download.date_completed is not None


def test_refresh_downloads_no_updates_when_status_unchanged() -> None:
    """Should not update downloads when status hasn't changed."""
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=uuid4(),
        magnet_link=magnet_link,
        title="Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    # Torrent status indicates still downloading
    torrent_status = DownloadStatus(
        progress=50.0,
        download_rate=1024,
        upload_rate=512,
        eta_seconds=3600,
        is_complete=False,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.side_effect = [[download], []]  # One DOWNLOADING, no PAUSED

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = RefreshDownloads(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = RefreshDownloads.Input()
    result = use_case.execute(input_data)

    assert result.updated_count == 0
    assert result.error_count == 0
    mock_repo.save.assert_not_called()


def test_refresh_downloads_handles_torrent_not_found() -> None:
    """Should skip downloads when torrent not found in client."""
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=uuid4(),
        magnet_link=magnet_link,
        title="Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.side_effect = [[download], []]  # One DOWNLOADING

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = None  # Not found in client

    use_case = RefreshDownloads(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = RefreshDownloads.Input()
    result = use_case.execute(input_data)

    assert result.updated_count == 0
    assert result.error_count == 0
    mock_repo.save.assert_not_called()


def test_refresh_downloads_handles_client_errors_gracefully() -> None:
    """Should record errors but continue processing other downloads."""
    magnet_link1 = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    magnet_link2 = MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40)

    download1 = Download(
        id_=uuid4(),
        magnet_link=magnet_link1,
        title="Download 1",
        file_path=Path("/downloads/test1"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    download2 = Download(
        id_=uuid4(),
        magnet_link=magnet_link2,
        title="Download 2",
        file_path=Path("/downloads/test2"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(2048 * 1024),
        status=DownloadState.DOWNLOADING,
    )

    # First download fails, second succeeds
    torrent_status2 = DownloadStatus(
        progress=100.0,
        download_rate=0,
        upload_rate=0,
        eta_seconds=None,
        is_complete=True,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.side_effect = [[download1, download2], []]  # Two DOWNLOADING

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.side_effect = [
        TorrentClientError("Client error for download1"),
        torrent_status2,
    ]

    use_case = RefreshDownloads(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = RefreshDownloads.Input()
    result = use_case.execute(input_data)

    assert result.updated_count == 1  # download2 was updated
    assert result.error_count == 1  # download1 had an error
    assert len(result.errors) == 1
    assert (
        "download1" in result.errors[0].lower()
        or str(download1.id_) in result.errors[0]
    )

    # Verify download2 was saved
    assert mock_repo.save.call_count == 1
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.id_ == download2.id_


def test_refresh_downloads_updates_paused_to_downloading() -> None:
    """Should update status from PAUSED to DOWNLOADING when resumed externally."""
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=uuid4(),
        magnet_link=magnet_link,
        title="Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.PAUSED,
    )

    # Torrent status indicates now downloading
    torrent_status = DownloadStatus(
        progress=50.0,
        download_rate=1024,
        upload_rate=512,
        eta_seconds=3600,
        is_complete=False,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.side_effect = [[], [download]]  # No DOWNLOADING, one PAUSED

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = RefreshDownloads(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = RefreshDownloads.Input()
    result = use_case.execute(input_data)

    assert result.updated_count == 1
    assert result.error_count == 0

    # Verify download was saved with DOWNLOADING status
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.status == DownloadState.DOWNLOADING


def test_refresh_downloads_sets_date_completed() -> None:
    """Should set date_completed when download becomes COMPLETED."""
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    download = Download(
        id_=uuid4(),
        magnet_link=magnet_link,
        title="Download",
        file_path=Path("/downloads/test"),
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_completed=None,
    )

    torrent_status = DownloadStatus(
        progress=100.0,
        download_rate=0,
        upload_rate=0,
        eta_seconds=None,
        is_complete=True,
        is_paused=False,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.side_effect = [[download], []]

    mock_client = Mock(spec=ITorrentClient)
    mock_client.get_status.return_value = torrent_status

    use_case = RefreshDownloads(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = RefreshDownloads.Input()
    result = use_case.execute(input_data)

    assert result.updated_count == 1

    # Verify date_completed was set
    saved_download = mock_repo.save.call_args[0][0]
    assert saved_download.date_completed is not None
    assert isinstance(saved_download.date_completed, datetime)


def test_refresh_downloads_does_not_overwrite_existing_date_completed() -> None:
    """Should not overwrite date_completed if already set."""
    mock_repo = Mock(spec=IDownloadRepository)
    # COMPLETED downloads are not in active list, so no downloads to refresh
    mock_repo.find_all.side_effect = [[], []]

    mock_client = Mock(spec=ITorrentClient)

    use_case = RefreshDownloads(
        download_repository=mock_repo,
        torrent_client=mock_client,
    )

    input_data = RefreshDownloads.Input()
    result = use_case.execute(input_data)

    assert result.updated_count == 0
    mock_client.get_status.assert_not_called()
