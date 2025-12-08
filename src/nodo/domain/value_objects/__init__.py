"""Domain value objects for the Nodo application."""

from nodo.domain.value_objects.aggregator_source import AggregatorSource
from nodo.domain.value_objects.download_status import DownloadStatus
from nodo.domain.value_objects.file_size import FileSize
from nodo.domain.value_objects.magnet_link import MagnetLink

__all__ = [
    "AggregatorSource",
    "DownloadStatus",
    "FileSize",
    "MagnetLink",
]
