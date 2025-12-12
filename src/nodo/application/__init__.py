"""Application layer for the Nodo application."""

from nodo.application.dtos import (
    DownloadDTO,
    TorrentSearchResultDTO,
)
from nodo.application.interfaces import (
    IDownloadRepository,
    IndexerManager,
    ITorrentClient,
    IUserPreferencesRepository,
)
from nodo.application.use_cases import (
    AddFavoriteIndexer,
    AddFavoritePath,
    GetUserPreferences,
    RemoveFavoriteIndexer,
    RemoveFavoritePath,
    UpdateUserPreferences,
)
from nodo.domain.entities import DownloadStatus

__all__ = [
    # DTOs
    "DownloadDTO",
    "TorrentSearchResultDTO",
    # Interfaces
    "IDownloadRepository",
    "IndexerManager",
    "ITorrentClient",
    "IUserPreferencesRepository",
    # Domain Entities
    "DownloadStatus",
    # Use Cases
    "AddFavoriteIndexer",
    "AddFavoritePath",
    "GetUserPreferences",
    "RemoveFavoriteIndexer",
    "RemoveFavoritePath",
    "UpdateUserPreferences",
]
