"""Torrent search result entity."""

from dataclasses import dataclass
from datetime import datetime

from nodo.domain.value_objects import AggregatorSource, FileSize, MagnetLink


@dataclass(frozen=True, slots=True, kw_only=True)
class TorrentSearchResult:
    """Represents a torrent found from an aggregator search.

    This is an ephemeral entity that exists only in memory during search
    operations. It is not persisted to the database but can be converted
    to a Download entity when the user selects it.

    Attributes:
        magnet_link: Unique identifier for the torrent.
        title: Name/title of the torrent.
        size: File size of the torrent.
        seeders: Number of seeders.
        leechers: Number of leechers.
        source: Which aggregator it came from.
        date_found: When this result was retrieved.
    """

    magnet_link: MagnetLink
    title: str
    size: FileSize
    seeders: int
    leechers: int
    source: AggregatorSource
    date_found: datetime
