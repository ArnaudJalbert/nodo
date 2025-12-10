"""Domain layer for the Nodo application."""

from nodo.domain.entities import (
    USER_PREFERENCES_ID,
    Download,
    DownloadStatus,
    TorrentSearchResult,
    UserPreferences,
)
from nodo.domain.exceptions import (
    AggregatorError,
    AggregatorTimeoutError,
    DomainError,
    DownloadNotFoundError,
    DuplicateDownloadError,
    FileSystemError,
    InvalidStateTransitionError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import (
    AggregatorSource,
    DownloadState,
    FileSize,
    MagnetLink,
)

__all__ = [
    # Entities
    "Download",
    "DownloadStatus",
    "TorrentSearchResult",
    "USER_PREFERENCES_ID",
    "UserPreferences",
    # Exceptions
    "AggregatorError",
    "AggregatorTimeoutError",
    "DomainError",
    "DownloadNotFoundError",
    "DuplicateDownloadError",
    "FileSystemError",
    "InvalidStateTransitionError",
    "TorrentClientError",
    "ValidationError",
    # Value Objects
    "AggregatorSource",
    "DownloadState",
    "FileSize",
    "MagnetLink",
]
