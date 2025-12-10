"""Domain entities for the Nodo application."""

from nodo.domain.entities.download import Download
from nodo.domain.entities.download_status import DownloadStatus
from nodo.domain.entities.torrent_search_result import TorrentSearchResult
from nodo.domain.entities.user_preferences import USER_PREFERENCES_ID, UserPreferences

__all__ = [
    "Download",
    "DownloadStatus",
    "TorrentSearchResult",
    "USER_PREFERENCES_ID",
    "UserPreferences",
]
