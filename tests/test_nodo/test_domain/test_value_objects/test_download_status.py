"""Tests for DownloadStatus enum."""

from nodo.domain.value_objects import DownloadStatus


def test_download_status_has_downloading() -> None:
    """DownloadStatus should have DOWNLOADING value."""
    assert DownloadStatus.DOWNLOADING is not None


def test_download_status_has_completed() -> None:
    """DownloadStatus should have COMPLETED value."""
    assert DownloadStatus.COMPLETED is not None


def test_download_status_has_failed() -> None:
    """DownloadStatus should have FAILED value."""
    assert DownloadStatus.FAILED is not None


def test_download_status_has_paused() -> None:
    """DownloadStatus should have PAUSED value."""
    assert DownloadStatus.PAUSED is not None


def test_download_status_all_values_are_unique() -> None:
    """All status values should be unique."""
    statuses = [
        DownloadStatus.DOWNLOADING,
        DownloadStatus.COMPLETED,
        DownloadStatus.FAILED,
        DownloadStatus.PAUSED,
    ]
    assert len(statuses) == len(set(statuses))


def test_download_status_equality() -> None:
    """Same status should be equal to itself."""
    assert DownloadStatus.DOWNLOADING == DownloadStatus.DOWNLOADING
    assert DownloadStatus.COMPLETED == DownloadStatus.COMPLETED


def test_download_status_inequality() -> None:
    """Different statuses should not be equal."""
    assert DownloadStatus.DOWNLOADING != DownloadStatus.COMPLETED
    assert DownloadStatus.PAUSED != DownloadStatus.FAILED
