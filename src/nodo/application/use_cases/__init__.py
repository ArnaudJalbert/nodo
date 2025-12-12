"""Use cases for the application layer."""

from nodo.application.use_cases.add_download import AddDownload
from nodo.application.use_cases.add_favorite_indexer import AddFavoriteIndexer
from nodo.application.use_cases.add_favorite_path import AddFavoritePath
from nodo.application.use_cases.get_download_status import GetDownloadStatus
from nodo.application.use_cases.get_user_preferences import GetUserPreferences
from nodo.application.use_cases.list_downloads import ListDownloads
from nodo.application.use_cases.pause_download import PauseDownload
from nodo.application.use_cases.refresh_downloads import RefreshDownloads
from nodo.application.use_cases.remove_download import RemoveDownload
from nodo.application.use_cases.remove_favorite_indexer import (
    RemoveFavoriteIndexer,
)
from nodo.application.use_cases.remove_favorite_path import RemoveFavoritePath
from nodo.application.use_cases.resume_download import ResumeDownload
from nodo.application.use_cases.search_torrents import SearchTorrents
from nodo.application.use_cases.update_user_preferences import UpdateUserPreferences

__all__ = [
    "GetUserPreferences",
    "UpdateUserPreferences",
    "AddFavoritePath",
    "RemoveFavoritePath",
    "AddFavoriteIndexer",
    "RemoveFavoriteIndexer",
    "ListDownloads",
    "AddDownload",
    "SearchTorrents",
    "GetDownloadStatus",
    "RemoveDownload",
    "PauseDownload",
    "ResumeDownload",
    "RefreshDownloads",
]
