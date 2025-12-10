"""Application layer for the Nodo application."""

from nodo.application.dtos import (
    DownloadDTO,
    TorrentSearchResultDTO,
)
from nodo.application.interfaces import (
    IAggregatorService,
    IDownloadRepository,
    ITorrentClient,
    IUserPreferencesRepository,
)
from nodo.domain.entities import DownloadStatus
from nodo.application.use_cases import (
    AddFavoriteAggregator,
    AddFavoritePath,
    GetUserPreferences,
    RemoveFavoriteAggregator,
    RemoveFavoritePath,
    UpdateUserPreferences,
)

__all__ = [
    # DTOs
    "DownloadDTO",
    "TorrentSearchResultDTO",
    # Interfaces
    "IAggregatorService",
    "IDownloadRepository",
    "ITorrentClient",
    "IUserPreferencesRepository",
    # Domain Entities
    "DownloadStatus",
    # Use Cases
    "AddFavoriteAggregator",
    "AddFavoritePath",
    "GetUserPreferences",
    "RemoveFavoriteAggregator",
    "RemoveFavoritePath",
    "UpdateUserPreferences",
]
