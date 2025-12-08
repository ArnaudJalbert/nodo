"""Domain layer for the Nodo application."""

from nodo.domain.entities import (
    USER_PREFERENCES_ID,
    Download,
    TorrentSearchResult,
    UserPreferences,
)
from nodo.domain.exceptions import (
    AggregatorError,
    AggregatorTimeoutError,
    DomainException,
    DownloadNotFoundError,
    DuplicateDownloadError,
    FileSystemError,
    InvalidStateTransitionError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import (
    AggregatorSource,
    DownloadStatus,
    FileSize,
    MagnetLink,
)

__all__ = [
    # Entities
    "Download",
    "TorrentSearchResult",
    "USER_PREFERENCES_ID",
    "UserPreferences",
    # Exceptions
    "AggregatorError",
    "AggregatorTimeoutError",
    "DomainException",
    "DownloadNotFoundError",
    "DuplicateDownloadError",
    "FileSystemError",
    "InvalidStateTransitionError",
    "TorrentClientError",
    "ValidationError",
    # Value Objects
    "AggregatorSource",
    "DownloadStatus",
    "FileSize",
    "MagnetLink",
]
