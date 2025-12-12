"""Application layer interfaces."""

from nodo.application.interfaces.download_repository import IDownloadRepository
from nodo.application.interfaces.file_system_repository import IFileSystemRepository
from nodo.application.interfaces.indexer_manager import IndexerManager
from nodo.application.interfaces.torrent_client import ITorrentClient
from nodo.application.interfaces.user_preferences_repository import (
    IUserPreferencesRepository,
)

__all__ = [
    "IDownloadRepository",
    "IFileSystemRepository",
    "IndexerManager",
    "ITorrentClient",
    "IUserPreferencesRepository",
]
