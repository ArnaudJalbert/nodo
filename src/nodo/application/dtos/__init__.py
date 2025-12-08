"""Data transfer objects for the application layer."""

from nodo.application.dtos.download_dto import DownloadDTO
from nodo.application.dtos.torrent_search_result_dto import TorrentSearchResultDTO
from nodo.application.dtos.user_preferences_dto import UserPreferencesDTO

__all__ = [
    "DownloadDTO",
    "TorrentSearchResultDTO",
    "UserPreferencesDTO",
]
