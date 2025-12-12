"""Search torrents use case."""

from dataclasses import dataclass

from nodo.application.dtos import TorrentSearchResultDTO
from nodo.application.interfaces import (
    IndexerManager,
    IUserPreferencesRepository,
)
from nodo.domain.entities import TorrentSearchResult
from nodo.domain.exceptions import (
    IndexerError,
    IndexerTimeoutError,
    ValidationError,
)


class SearchTorrents:
    """Use case for searching torrents via indexer manager.

    Searches through a unified indexer manager interface, handles
    results, and returns sorted results.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for SearchTorrents use case.

        Attributes:
            query: Search query string.
            indexer_names: Optional list of indexer names to search.
                If None, uses favorite indexers from preferences.
                If provided, must contain at least one indexer name.
            max_results: Maximum number of results per indexer.
        """

        query: str
        indexer_names: list[str] | None = None
        max_results: int = 10

    @dataclass(frozen=True, slots=True, kw_only=True)
    class FailedSearch:
        """DTO for a failed indexer search.

        Attributes:
            indexer_name: Name of the indexer that failed.
            error_message: Error message from the failure.
        """

        indexer_name: str
        error_message: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for SearchTorrents use case.

        Attributes:
            results: List of search result DTOs.
            failed_searches: List of failed indexer searches.
        """

        results: tuple[TorrentSearchResultDTO, ...]
        failed_searches: tuple["SearchTorrents.FailedSearch", ...]

    def __init__(
        self,
        indexer_manager: IndexerManager,
        preferences_repository: IUserPreferencesRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            indexer_manager: Indexer manager for searching.
            preferences_repository: Repository for user preferences.
        """
        self._indexer_manager = indexer_manager
        self._preferences_repository = preferences_repository

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing search criteria.

        Returns:
            Output containing search results.

        Raises:
            ValidationError: If query is empty or invalid.
            IndexerError: If search fails.
            IndexerTimeoutError: If search times out.
        """
        # Validate query
        if not input_data.query or not input_data.query.strip():
            raise ValidationError("Search query cannot be empty")

        query = input_data.query.strip()

        # Validate max_results
        if input_data.max_results < 1:
            raise ValidationError("max_results must be at least 1")

        # Validate indexer_names if provided
        if input_data.indexer_names is not None:
            if len(input_data.indexer_names) == 0:
                raise ValidationError(
                    "indexer_names must contain at least one indexer name"
                )

        # Determine which indexers to use
        indexer_names = self._determine_indexers_to_search(input_data.indexer_names)

        if not indexer_names:
            raise IndexerError("No indexers available for search")

        # Validate that all provided indexer names are valid
        if input_data.indexer_names is not None:
            available_names = set(self._indexer_manager.get_available_indexers())
            invalid_indexers = [
                name for name in input_data.indexer_names if name not in available_names
            ]
            if invalid_indexers:
                valid_names = ", ".join(sorted(available_names))
                raise ValidationError(
                    f"Invalid indexer names: {', '.join(invalid_indexers)}. "
                    f"Valid indexers are: {valid_names}"
                )

        # Search via indexer manager
        try:
            results = self._indexer_manager.search(
                query=query,
                indexer_names=indexer_names,
                max_results=input_data.max_results,
            )
        except IndexerTimeoutError:
            raise
        except IndexerError:
            raise

        # Sort by seeders (descending)
        sorted_results = sorted(results, key=lambda r: r.seeders, reverse=True)

        # Convert to DTOs
        result_dtos = tuple(SearchTorrents._to_dto(result) for result in sorted_results)
        failed_dtos = tuple()  # Indexer manager handles failures internally

        return SearchTorrents.Output(results=result_dtos, failed_searches=failed_dtos)

    def _determine_indexers_to_search(
        self, provided_names: list[str] | None
    ) -> list[str]:
        """Determine which indexers to search.

        Args:
            provided_names: Optional list of indexer names from input.
                If None, uses preferences or all available indexers.
                If provided, must contain at least one name (validated in execute).

        Returns:
            List of indexer names to search.
        """
        if provided_names is not None:
            return provided_names

        # Get from preferences
        preferences = self._preferences_repository.get()
        favorite_indexers = preferences.favorite_indexers

        # If favorites exist, use them; otherwise use all available
        if favorite_indexers:
            return [str(idx) for idx in favorite_indexers]

        # Return all available indexer names
        return self._indexer_manager.get_available_indexers()

    @staticmethod
    def _to_dto(result: TorrentSearchResult) -> TorrentSearchResultDTO:
        """Convert TorrentSearchResult entity to DTO.

        Args:
            result: The search result entity to convert.

        Returns:
            TorrentSearchResultDTO representation of the entity.
        """
        return TorrentSearchResultDTO(
            magnet_link=str(result.magnet_link),
            title=result.title,
            size=str(result.size),
            seeders=result.seeders,
            leechers=result.leechers,
            source=str(result.source),
            date_found=result.date_found,
        )
