"""Domain value objects for the Nodo application."""

from nodo.domain.value_objects.download_state import DownloadState
from nodo.domain.value_objects.file_size import FileSize
from nodo.domain.value_objects.indexer_source import IndexerSource
from nodo.domain.value_objects.magnet_link import MagnetLink, TorrentLink
from nodo.domain.value_objects.time_duration import TimeDuration

__all__ = [
    "DownloadState",
    "FileSize",
    "IndexerSource",
    "MagnetLink",
    "TorrentLink",
    "TimeDuration",
]
