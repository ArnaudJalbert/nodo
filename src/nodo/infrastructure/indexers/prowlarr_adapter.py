"""Prowlarr indexer source adapter."""

from typing import Any

import requests

from nodo.domain.exceptions import IndexerError, IndexerTimeoutError


class ProwlarrAdapter:
    """Prowlarr indexer source implementation.

    Implements IIndexerSourceProtocol using the Prowlarr API to search
    multiple indexers and return raw result dictionaries.
    Data mapping to domain entities is handled by IndexerSourceAdapter
    in the interface adapters layer.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
    ) -> None:
        """Initialize Prowlarr adapter.

        Args:
            base_url: Prowlarr instance URL (e.g., "http://localhost:9696")
            api_key: Prowlarr API key
            timeout: Request timeout in seconds

        Raises:
            ValueError: If base_url or api_key is empty
        """
        if not base_url or not base_url.strip():
            raise ValueError("base_url cannot be empty")
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")

        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"X-Api-Key": api_key})

    def search(
        self,
        query: str,
        indexer_names: list[str] | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for torrents via Prowlarr API.

        Args:
            query: Search query string.
            indexer_names: Optional list of indexer names to search.
            max_results: Maximum results per indexer.

        Returns:
            List of raw search result dictionaries from Prowlarr API.

        Raises:
            IndexerError: If the search fails.
            IndexerTimeoutError: If the search times out.
        """
        try:
            # Build search params
            params = {
                "query": query,
                "limit": max_results,
            }

            # Make request to Prowlarr search endpoint
            response = self._session.get(
                f"{self._base_url}/api/v1/search",
                params=params,
                timeout=self._timeout,
            )

            # Check for HTTP errors
            if response.status_code != 200:
                raise IndexerError(
                    f"Prowlarr API error {response.status_code}: {response.text}"
                )

            # Parse response
            data = response.json()
            if not isinstance(data, list):
                raise IndexerError(
                    f"Unexpected Prowlarr API response format: {type(data)}"
                )

            # Return raw results (mapping happens in interface adapter)
            return data

        except requests.Timeout:
            raise IndexerTimeoutError(
                f"Prowlarr search timed out after {self._timeout}s"
            )
        except requests.RequestException as e:
            raise IndexerError(f"Prowlarr API request failed: {e}")

    def get_available_indexers(self) -> list[str]:
        """Get list of available indexers from Prowlarr.

        Returns:
            List of available indexer names.

        Raises:
            IndexerError: If the request fails.
        """
        try:
            response = self._session.get(
                f"{self._base_url}/api/v1/indexer",
                timeout=self._timeout,
            )

            if response.status_code != 200:
                raise IndexerError(
                    f"Prowlarr API error {response.status_code}: {response.text}"
                )

            data = response.json()
            if not isinstance(data, list):
                raise IndexerError(
                    f"Unexpected Prowlarr API response format: {type(data)}"
                )

            # Extract indexer names
            indexer_names = []
            for item in data:
                if isinstance(item, dict) and "name" in item:
                    indexer_names.append(item["name"])

            return indexer_names

        except requests.RequestException as e:
            raise IndexerError(f"Prowlarr API request failed: {e}")
