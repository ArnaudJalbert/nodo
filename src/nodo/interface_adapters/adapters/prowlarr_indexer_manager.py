"""Prowlarr indexer manager adapter implementation."""

from datetime import datetime
from typing import Any

from nodo.application.interfaces import IndexerManager
from nodo.domain.entities import TorrentSearchResult
from nodo.domain.value_objects import FileSize, IndexerSource, TorrentLink
from nodo.interface_adapters.protocols.prowlarr_source_protocol import (
    IProwlarrSource,
)


class ProwlarrIndexerManager(IndexerManager):
    """Prowlarr indexer manager adapter.

    Inherits from IndexerManager abstract base class and implements
    concrete functionality by wrapping a Prowlarr source.

    Maps raw dictionary results from IProwlarrSource
    (e.g., ProwlarrAdapter) to TorrentSearchResult domain entities.
    This adapter is responsible for all data transformation and validation
    at the boundary between infrastructure and application layers.
    """

    def __init__(self, indexer_source: IProwlarrSource) -> None:
        """Initialize the Prowlarr indexer manager.

        Args:
            indexer_source: The underlying Prowlarr source service.
        """
        self._indexer_source = indexer_source

    def search(
        self,
        query: str,
        indexer_names: list[str] | None = None,
        max_results: int = 10,
    ) -> list[TorrentSearchResult]:
        """Search for torrents and map results to domain entities.

        Args:
            query: Search query string.
            indexer_names: Optional list of specific indexer names to search.
            max_results: Maximum results per indexer.

        Returns:
            List of TorrentSearchResult domain entities.

        Raises:
            IndexerError: If the search fails.
            IndexerTimeoutError: If the search times out.
        """
        raw_results = self._indexer_source.search(
            query=query,
            indexer_names=indexer_names,
            max_results=max_results,
        )

        # Map raw results to domain entities, skipping malformed ones
        entities = []
        for raw_result in raw_results:
            try:
                entity = self._map_to_entity(raw_result)
                entities.append(entity)
            except (ValueError, KeyError, TypeError):
                # Skip malformed results
                continue

        return entities

    def get_available_indexers(self) -> list[str]:
        """Get available indexers from the source.

        Returns:
            List of available indexer names.
        """
        return self._indexer_source.get_available_indexers()

    @staticmethod
    def _map_to_entity(raw_result: dict[str, Any]) -> TorrentSearchResult:
        """Map raw indexer result dictionary to TorrentSearchResult entity.

        Args:
            raw_result: Raw result dictionary from indexer source.

        Returns:
            TorrentSearchResult domain entity.

        Raises:
            ValueError: If required fields are missing or invalid.
            KeyError: If result structure is unexpected.
        """
        # Extract required fields with fallbacks
        magnet_link_str = raw_result.get("magnetUrl") or raw_result.get("guid")
        if not magnet_link_str:
            raise ValueError("Missing magnet URL in result")

        title = raw_result.get("title")
        if not title:
            raise ValueError("Missing title in result")

        size_bytes = raw_result.get("size", 0)
        seeders = raw_result.get("seeders", 0)
        leechers = raw_result.get("leechers", 0) or raw_result.get("peers", 0)
        indexer_name = raw_result.get("indexer", "Unknown")
        publish_date_str = raw_result.get("publishDate")

        # Parse date
        if publish_date_str:
            try:
                date_found = datetime.fromisoformat(
                    publish_date_str.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError, TypeError):
                date_found = datetime.now()
        else:
            date_found = datetime.now()

        # Create domain entities
        magnet_link = TorrentLink.from_string(magnet_link_str)
        file_size = FileSize(bytes_=size_bytes)
        source = IndexerSource.from_string(indexer_name)

        return TorrentSearchResult(
            magnet_link=magnet_link,
            title=title,
            size=file_size,
            seeders=int(seeders),
            leechers=int(leechers),
            source=source,
            date_found=date_found,
        )
