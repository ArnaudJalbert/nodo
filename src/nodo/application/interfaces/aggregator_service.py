"""Aggregator service interface."""

from abc import ABC, abstractmethod

from nodo.domain.entities import TorrentSearchResult
from nodo.domain.value_objects import AggregatorSource


class IAggregatorService(ABC):
    """Interface for torrent aggregator search operations.

    This abstract base class defines the contract for searching
    torrents across external aggregator services.
    """

    @property
    @abstractmethod
    def source(self) -> AggregatorSource:
        """Get the aggregator source this service represents.

        Returns:
            The aggregator source.
        """

    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> list[TorrentSearchResult]:
        """Search for torrents matching the query.

        Args:
            query: The search query string.
            max_results: Maximum number of results to return.

        Returns:
            List of torrent search results.

        Raises:
            AggregatorError: If the search fails.
            AggregatorTimeoutError: If the search times out.
        """
