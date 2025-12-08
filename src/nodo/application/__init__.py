"""Application layer for the Nodo application."""

from nodo.application.dtos import (
    DownloadDTO,
    TorrentSearchResultDTO,
    UserPreferencesDTO,
)
from nodo.application.interfaces import (
    IAggregatorService,
    IDownloadRepository,
    ITorrentClient,
    IUserPreferencesRepository,
    TorrentStatus,
)

__all__ = [
    # DTOs
    "DownloadDTO",
    "TorrentSearchResultDTO",
    "UserPreferencesDTO",
    # Interfaces
    "IAggregatorService",
    "IDownloadRepository",
    "ITorrentClient",
    "IUserPreferencesRepository",
    "TorrentStatus",
]
