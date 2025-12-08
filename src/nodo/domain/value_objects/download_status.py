"""Download status enumeration."""

from enum import Enum, auto


class DownloadStatus(Enum):
    """Represents the current status of a download.

    Attributes:
        DOWNLOADING: The download is currently in progress.
        COMPLETED: The download has finished successfully.
        FAILED: The download has failed.
        PAUSED: The download has been paused by the user.
    """

    DOWNLOADING = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()
