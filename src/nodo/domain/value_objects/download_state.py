"""Download state enumeration."""

from enum import Enum, auto


class DownloadState(Enum):
    """Represents the current state of a download.

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
