"""Application layer interfaces."""

from nodo.application.interfaces.aggregator_service import IAggregatorService
from nodo.application.interfaces.aggregator_service_registry import (
    IAggregatorServiceRegistry,
)
from nodo.application.interfaces.download_repository import IDownloadRepository
from nodo.application.interfaces.torrent_client import ITorrentClient, TorrentStatus
from nodo.application.interfaces.user_preferences_repository import (
    IUserPreferencesRepository,
)

__all__ = [
    "IAggregatorService",
    "IAggregatorServiceRegistry",
    "IDownloadRepository",
    "ITorrentClient",
    "IUserPreferencesRepository",
    "TorrentStatus",
]
