"""Torrent search result data transfer object."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class TorrentSearchResultDTO:
    """Data transfer object for TorrentSearchResult entity.

    Used to transfer search result data between layers without exposing
    the domain entity directly.

    Attributes:
        magnet_link: The magnet link URI.
        title: Name/title of the torrent.
        size: Human-readable size string.
        seeders: Number of seeders.
        leechers: Number of leechers.
        source: Which indexer it came from.
        date_found: When this result was retrieved.
    """

    magnet_link: str
    title: str
    size: str
    seeders: int
    leechers: int
    source: str
    date_found: datetime
