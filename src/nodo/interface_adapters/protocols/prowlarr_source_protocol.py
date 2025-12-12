"""Protocol for Prowlarr source that returns raw data."""

from typing import Any, Protocol


class IProwlarrSource(Protocol):
    """Protocol for Prowlarr source services that return raw indexer data.

    Defines the interface for Prowlarr API services that provide raw torrent search
    results without any domain entity mapping. The raw data is returned as dictionaries.

    This protocol lives in the interface adapters layer because it defines
    the boundary between raw Prowlarr API data and domain entity mapping.
    """

    def search(
        self,
        query: str,
        indexer_names: list[str] | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for torrents via Prowlarr API.

        Args:
            query: Search query string.
            indexer_names: Optional list of specific indexer names to search.
            max_results: Maximum results per indexer.

        Returns:
            List of raw search result dictionaries from Prowlarr API.

        Raises:
            IndexerError: If the search fails.
            IndexerTimeoutError: If the search times out.
        """
        ...  # pragma: no cover

    def get_available_indexers(self) -> list[str]:
        """Get list of available indexers from Prowlarr.

        Returns:
            List of available indexer names.
        """
        ...  # pragma: no cover
