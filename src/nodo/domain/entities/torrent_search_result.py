"""Torrent search result entity."""

from dataclasses import dataclass
from datetime import datetime

from nodo.domain.value_objects import FileSize, IndexerSource, TorrentLink


@dataclass(frozen=True, slots=True, kw_only=True)
class TorrentSearchResult:
    """Represents a torrent found from an indexer search.

    This is an ephemeral entity that exists only in memory during search
    operations. It is not persisted to the database but can be converted
    to a Download entity when the user selects it.

    Attributes:
        magnet_link: Torrent link (magnet URI or HTTP/HTTPS URL) for the torrent.
        title: Name/title of the torrent.
        size: File size of the torrent.
        seeders: Number of seeders.
        leechers: Number of leechers.
        source: Which indexer it came from.
        date_found: When this result was retrieved.
    """

    magnet_link: TorrentLink
    title: str
    size: FileSize
    seeders: int
    leechers: int
    source: IndexerSource
    date_found: datetime

    def __hash__(self) -> int:
        """Hash based on magnet link for deduplication."""
        return hash(self.magnet_link)

    def __eq__(self, other: object) -> bool:
        """Two results are equal if they have the same magnet link."""
        if not isinstance(other, TorrentSearchResult):
            return NotImplemented
        return self.magnet_link == other.magnet_link
