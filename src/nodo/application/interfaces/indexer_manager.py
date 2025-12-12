"""Indexer manager abstract base class."""

from abc import ABC, abstractmethod

from nodo.domain.entities import TorrentSearchResult


class IndexerManager(ABC):
    """Abstract base class for indexer manager services.

    Defines the interface for services that manage indexer sources
    and provide domain-mapped torrent search results.
    """

    @abstractmethod
    def search(
        self,
        query: str,
        indexer_names: list[str] | None = None,
        max_results: int = 10,
    ) -> list[TorrentSearchResult]:
        """Search for torrents and return domain entities.

        Args:
            query: Search query string.
            indexer_names: Optional list of specific indexer names to search.
                          If None, searches all configured indexers.
            max_results: Maximum results per indexer.

        Returns:
            List of TorrentSearchResult domain entities.

        Raises:
            IndexerError: If the search fails.
            IndexerTimeoutError: If the search times out.
        """
        ...  # pragma: no cover

    @abstractmethod
    def get_available_indexers(self) -> list[str]:
        """Get list of available indexer names from the source.

        Returns:
            List of available indexer names.
        """
        ...  # pragma: no cover
