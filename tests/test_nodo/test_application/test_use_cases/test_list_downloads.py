"""Tests for ListDownloads use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest

from nodo.application.interfaces import IDownloadRepository
from nodo.application.use_cases.list_downloads import ListDownloads
from nodo.domain.entities import Download
from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import (
    AggregatorSource,
    DownloadState,
    FileSize,
    MagnetLink,
)


def test_list_downloads_returns_all_downloads() -> None:
    """Should return all downloads when no filter is specified."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Test Download 1",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Test Download 2",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("ThePirateBay"),
        size=FileSize.from_bytes(2048 * 1024),
        status=DownloadState.COMPLETED,
        date_added=datetime(2025, 1, 2, 12, 0, 0),
        date_completed=datetime(2025, 1, 2, 13, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input()
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    # Default sort is by date_added descending, so newer download comes first
    assert result.downloads[0].title == "Test Download 2"
    assert result.downloads[1].title == "Test Download 1"
    mock_repo.find_all.assert_called_once_with(status=None)


def test_list_downloads_filters_by_status() -> None:
    """Should filter downloads by status."""
    download = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(status="DOWNLOADING")
    result = use_case.execute(input_data)

    assert len(result.downloads) == 1
    assert result.downloads[0].status == "DOWNLOADING"
    mock_repo.find_all.assert_called_once_with(status=DownloadState.DOWNLOADING)


def test_list_downloads_sorts_by_date_added_descending() -> None:
    """Should sort downloads by date_added in descending order by default."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Older Download",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Newer Download",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 2, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="date_added", ascending=False)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    assert result.downloads[0].title == "Newer Download"
    assert result.downloads[1].title == "Older Download"


def test_list_downloads_sorts_by_date_added_ascending() -> None:
    """Should sort downloads by date_added in ascending order when specified."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Older Download",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Newer Download",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 2, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="date_added", ascending=True)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    assert result.downloads[0].title == "Older Download"
    assert result.downloads[1].title == "Newer Download"


def test_list_downloads_sorts_by_id() -> None:
    """Should sort downloads by id."""
    id1 = uuid4()
    id2 = uuid4()
    # Ensure id1 < id2 for consistent sorting
    if str(id1) > str(id2):
        id1, id2 = id2, id1

    download1 = Download(
        id_=id1,
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Download 1",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=id2,
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Download 2",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download2, download1]  # Reverse order

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="id_", ascending=True)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    assert result.downloads[0].id_ == str(id1)
    assert result.downloads[1].id_ == str(id2)


def test_list_downloads_sorts_by_title() -> None:
    """Should sort downloads by title."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Zebra Download",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Apple Download",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="title", ascending=True)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    assert result.downloads[0].title == "Apple Download"
    assert result.downloads[1].title == "Zebra Download"


def test_list_downloads_sorts_by_size() -> None:
    """Should sort downloads by size."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Small Download",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Large Download",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(2048 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="size", ascending=True)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    assert result.downloads[0].title == "Small Download"
    assert result.downloads[1].title == "Large Download"


def test_list_downloads_sorts_by_source() -> None:
    """Should sort downloads by source."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Zebra Download",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("ThePirateBay"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Apple Download",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="source", ascending=True)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    assert result.downloads[0].source == "1337x"
    assert result.downloads[1].source == "ThePirateBay"


def test_list_downloads_sorts_by_status() -> None:
    """Should sort downloads by status."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Failed Download",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.FAILED,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Completed Download",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.COMPLETED,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="status", ascending=True)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 2
    assert result.downloads[0].status == "COMPLETED"
    assert result.downloads[1].status == "FAILED"


def test_list_downloads_sorts_by_date_completed() -> None:
    """Should sort downloads by date_completed."""
    download1 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Earlier Completed",
        file_path=Path("/downloads/test1"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.COMPLETED,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
        date_completed=datetime(2025, 1, 1, 13, 0, 0),
    )
    download2 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Later Completed",
        file_path=Path("/downloads/test2"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.COMPLETED,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
        date_completed=datetime(2025, 1, 1, 14, 0, 0),
    )
    download3 = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "c" * 40),
        title="Not Completed",
        file_path=Path("/downloads/test3"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
        date_completed=None,
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download1, download2, download3]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="date_completed", ascending=True)
    result = use_case.execute(input_data)

    assert len(result.downloads) == 3
    # Downloads without date_completed should come first (datetime.min)
    assert result.downloads[0].title == "Not Completed"
    assert result.downloads[1].title == "Earlier Completed"
    assert result.downloads[2].title == "Later Completed"


def test_list_downloads_raises_error_for_invalid_status() -> None:
    """Should raise ValidationError for invalid status."""
    mock_repo = Mock(spec=IDownloadRepository)

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(status="INVALID_STATUS")

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "Invalid status" in str(exc_info.value)
    assert "INVALID_STATUS" in str(exc_info.value)


def test_list_downloads_raises_error_for_invalid_sort_by() -> None:
    """Should raise ValidationError for invalid sort_by field."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = []

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input(sort_by="invalid_field")

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "Invalid sort_by field" in str(exc_info.value)
    assert "invalid_field" in str(exc_info.value)


def test_list_downloads_returns_empty_list() -> None:
    """Should return empty list when no downloads exist."""
    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = []

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input()
    result = use_case.execute(input_data)

    assert len(result.downloads) == 0
    assert isinstance(result.downloads, tuple)


def test_list_downloads_converts_to_dto() -> None:
    """Should convert Download entities to DownloadDTOs."""
    download = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock(spec=IDownloadRepository)
    mock_repo.find_all.return_value = [download]

    use_case = ListDownloads(download_repository=mock_repo)
    input_data = ListDownloads.Input()
    result = use_case.execute(input_data)

    assert len(result.downloads) == 1
    dto = result.downloads[0]
    assert dto.id_ == str(download.id_)
    assert dto.magnet_link == str(download.magnet_link)
    assert dto.title == download.title
    assert dto.file_path == str(download.file_path)
    assert dto.source == str(download.source)
    assert dto.status == download.status.name
    assert dto.date_added == download.date_added
    assert dto.date_completed == download.date_completed
    assert dto.size == str(download.size)


def test_sort_downloads_raises_error_for_unsupported_field() -> None:
    """Should raise ValidationError when _sort_downloads receives unsupported field."""
    download = Download(
        id_=uuid4(),
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Test Download",
        file_path=Path("/downloads/test"),
        source=AggregatorSource.from_string("1337x"),
        size=FileSize.from_bytes(1024 * 1024),
        status=DownloadState.DOWNLOADING,
        date_added=datetime(2025, 1, 1, 12, 0, 0),
    )

    with pytest.raises(ValidationError) as exc_info:
        ListDownloads._sort_downloads([download], "unsupported_field", False)

    assert "Unsupported sort_by field" in str(exc_info.value)
    assert "unsupported_field" in str(exc_info.value)
