"""Tests for DownloadState enum."""

from nodo.domain.value_objects import DownloadState


def test_download_state_has_downloading() -> None:
    """DownloadState should have DOWNLOADING value."""
    assert DownloadState.DOWNLOADING is not None


def test_download_state_has_completed() -> None:
    """DownloadState should have COMPLETED value."""
    assert DownloadState.COMPLETED is not None


def test_download_state_has_failed() -> None:
    """DownloadState should have FAILED value."""
    assert DownloadState.FAILED is not None


def test_download_state_has_paused() -> None:
    """DownloadState should have PAUSED value."""
    assert DownloadState.PAUSED is not None


def test_download_state_all_values_are_unique() -> None:
    """All state values should be unique."""
    states = [
        DownloadState.DOWNLOADING,
        DownloadState.COMPLETED,
        DownloadState.FAILED,
        DownloadState.PAUSED,
    ]
    assert len(states) == len(set(states))


def test_download_state_equality() -> None:
    """Same state should be equal to itself."""
    assert DownloadState.DOWNLOADING == DownloadState.DOWNLOADING
    assert DownloadState.COMPLETED == DownloadState.COMPLETED


def test_download_state_inequality() -> None:
    """Different states should not be equal."""
    assert DownloadState.DOWNLOADING != DownloadState.COMPLETED
    assert DownloadState.PAUSED != DownloadState.FAILED
