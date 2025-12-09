"""Use cases for the application layer."""

from nodo.application.use_cases.add_download import AddDownload
from nodo.application.use_cases.add_favorite_aggregator import AddFavoriteAggregator
from nodo.application.use_cases.add_favorite_path import AddFavoritePath
from nodo.application.use_cases.get_user_preferences import GetUserPreferences
from nodo.application.use_cases.list_downloads import ListDownloads
from nodo.application.use_cases.remove_favorite_aggregator import (
    RemoveFavoriteAggregator,
)
from nodo.application.use_cases.remove_favorite_path import RemoveFavoritePath
from nodo.application.use_cases.search_torrents import SearchTorrents
from nodo.application.use_cases.update_user_preferences import UpdateUserPreferences

__all__ = [
    "GetUserPreferences",
    "UpdateUserPreferences",
    "AddFavoritePath",
    "RemoveFavoritePath",
    "AddFavoriteAggregator",
    "RemoveFavoriteAggregator",
    "ListDownloads",
    "AddDownload",
    "SearchTorrents",
]
