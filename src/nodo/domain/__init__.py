"""Domain layer for the Nodo application."""

from nodo.domain.entities import (
    USER_PREFERENCES_ID,
    Download,
    DownloadStatus,
    TorrentSearchResult,
    UserPreferences,
)
from nodo.domain.exceptions import (
    DomainError,
    DownloadNotFoundError,
    DuplicateDownloadError,
    FileSystemError,
    IndexerError,
    IndexerTimeoutError,
    InvalidStateTransitionError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import (
    DownloadState,
    FileSize,
    IndexerSource,
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
    "DomainError",
    "DownloadNotFoundError",
    "DuplicateDownloadError",
    "FileSystemError",
    "IndexerError",
    "IndexerTimeoutError",
    "InvalidStateTransitionError",
    "TorrentClientError",
    "ValidationError",
    # Value Objects
    "DownloadState",
    "FileSize",
    "IndexerSource",
    "MagnetLink",
]
