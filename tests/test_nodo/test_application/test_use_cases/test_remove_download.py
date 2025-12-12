"""Tests for RemoveDownload use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import (
    IDownloadRepository,
    IFileSystemRepository,
    ITorrentClient,
)
from nodo.application.use_cases.remove_download import RemoveDownload
from nodo.domain.entities import Download
from nodo.domain.exceptions import (
    DownloadNotFoundError,
    FileSystemError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import (
    DownloadState,
    FileSize,
    IndexerSource,
    MagnetLink,
)


def test_remove_download_success() -> None:
    """Should successfully remove a download."""
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
    mock_repo.delete.return_value = True

    mock_client = Mock(spec=ITorrentClient)
    mock_client.remove.return_value = True

    mock_fs = Mock(spec=IFileSystemRepository)

    use_case = RemoveDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
        file_system_repository=mock_fs,
    )

    input_data = RemoveDownload.Input(download_id=str(download_id))
    result = use_case.execute(input_data)

    assert isinstance(result.download, DownloadDTO)
    assert result.removed is True
    mock_repo.find_by_id.assert_called_once_with(download_id)
    mock_client.remove.assert_called_once_with(torrent_hash, delete_files=False)
    mock_repo.delete.assert_called_once_with(download_id)


def test_remove_download_with_file_deletion() -> None:
    """Should remove download and delete files when delete_files=True."""
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
        status=DownloadState.COMPLETED,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.delete.return_value = True

    mock_client = Mock(spec=ITorrentClient)
    mock_client.remove.return_value = True

    mock_fs = Mock(spec=IFileSystemRepository)

    use_case = RemoveDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
        file_system_repository=mock_fs,
    )

    input_data = RemoveDownload.Input(download_id=str(download_id), delete_files=True)
    result = use_case.execute(input_data)

    assert result.removed is True
    mock_client.remove.assert_called_once_with(torrent_hash, delete_files=True)
    mock_repo.delete.assert_called_once_with(download_id)


def test_remove_download_raises_error_for_invalid_uuid() -> None:
    """Should raise ValidationError for invalid UUID format."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_client = Mock(spec=ITorrentClient)
    mock_fs = Mock(spec=IFileSystemRepository)

    use_case = RemoveDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
        file_system_repository=mock_fs,
    )

    input_data = RemoveDownload.Input(download_id="invalid-uuid")

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "invalid download id format" in str(exc_info.value).lower()
    mock_repo.find_by_id.assert_not_called()
    mock_client.remove.assert_not_called()


def test_remove_download_raises_error_for_not_found() -> None:
    """Should raise DownloadNotFoundError when download not found."""
    download_id = uuid4()

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = None

    mock_client = Mock(spec=ITorrentClient)
    mock_fs = Mock(spec=IFileSystemRepository)

    use_case = RemoveDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
        file_system_repository=mock_fs,
    )

    input_data = RemoveDownload.Input(download_id=str(download_id))

    with pytest.raises(DownloadNotFoundError) as exc_info:
        use_case.execute(input_data)

    assert "not found" in str(exc_info.value).lower()
    mock_client.remove.assert_not_called()
    mock_repo.delete.assert_not_called()


def test_remove_download_raises_error_for_torrent_client_failure() -> None:
    """Should raise TorrentClientError when client removal fails."""
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
    mock_client.remove.side_effect = TorrentClientError("Client error")

    mock_fs = Mock(spec=IFileSystemRepository)

    use_case = RemoveDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
        file_system_repository=mock_fs,
    )

    input_data = RemoveDownload.Input(download_id=str(download_id))

    with pytest.raises(TorrentClientError) as exc_info:
        use_case.execute(input_data)

    assert "torrent client" in str(exc_info.value).lower()
    mock_repo.delete.assert_not_called()


def test_remove_download_deletes_files_when_client_does_not() -> None:
    """Should delete files manually when client doesn't handle deletion."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    torrent_hash = magnet_link.info_hash
    file_path = Path("/downloads/test_file.txt")

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=file_path,
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.COMPLETED,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download
    mock_repo.delete.return_value = True

    mock_client = Mock(spec=ITorrentClient)
    # Client returns False (didn't remove), but we still want to delete files
    mock_client.remove.return_value = False

    mock_fs = Mock(spec=IFileSystemRepository)

    use_case = RemoveDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
        file_system_repository=mock_fs,
    )

    input_data = RemoveDownload.Input(download_id=str(download_id), delete_files=True)
    result = use_case.execute(input_data)

    assert result.removed is True
    mock_client.remove.assert_called_once_with(torrent_hash, delete_files=True)
    mock_fs.delete_path.assert_called_once_with(file_path)
    mock_repo.delete.assert_called_once_with(download_id)


def test_remove_download_raises_error_for_file_deletion_failure() -> None:
    """Should raise FileSystemError when file deletion fails."""
    download_id = uuid4()
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    file_path = Path("/downloads/test_file.txt")

    download = Download(
        id_=download_id,
        magnet_link=magnet_link,
        title="Test Download",
        file_path=file_path,
        source=IndexerSource.from_string("Prowlarr"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.COMPLETED,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_by_id.return_value = download

    mock_client = Mock(spec=ITorrentClient)
    mock_client.remove.return_value = False  # Client didn't delete

    mock_fs = Mock(spec=IFileSystemRepository)
    mock_fs.delete_path.side_effect = FileSystemError("Permission denied")

    use_case = RemoveDownload(
        download_repository=mock_repo,
        torrent_client=mock_client,
        file_system_repository=mock_fs,
    )

    input_data = RemoveDownload.Input(download_id=str(download_id), delete_files=True)

    with pytest.raises(FileSystemError) as exc_info:
        use_case.execute(input_data)

    assert "permission denied" in str(exc_info.value).lower()
    mock_repo.delete.assert_not_called()


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
        status=DownloadState.COMPLETED,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
        date_completed=datetime(2025, 1, 1, 13, 0, 0),
    )

    dto = RemoveDownload._to_dto(download)

    assert dto.id_ == str(download_id)
    assert dto.magnet_link == str(magnet_link)
    assert dto.title == "Test Download"
    assert dto.file_path == str(file_path)
    assert dto.source == str(source)
    assert dto.size == str(size)
    assert dto.status == "COMPLETED"
    assert dto.date_added == datetime(2025, 1, 1, 12, 0, 0)
    assert dto.date_completed == datetime(2025, 1, 1, 13, 0, 0)
