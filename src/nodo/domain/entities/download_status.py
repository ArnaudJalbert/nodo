"""Download status entity."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadStatus:
    """Status information for a download from the torrent client.

    Attributes:
        progress: Download progress as percentage (0.0 to 100.0).
        download_rate: Current download speed in bytes per second.
        upload_rate: Current upload speed in bytes per second.
        eta_seconds: Estimated time remaining in seconds, None if unknown.
        is_complete: Whether the download is complete.
        is_paused: Whether the download is paused.
    """

    progress: float
    download_rate: int
    upload_rate: int
    eta_seconds: int | None
    is_complete: bool
    is_paused: bool
