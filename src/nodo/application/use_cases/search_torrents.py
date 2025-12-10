"""Search torrents use case."""

from dataclasses import dataclass

from nodo.application.dtos import TorrentSearchResultDTO
from nodo.application.interfaces import (
    IAggregatorServiceRegistry,
    IUserPreferencesRepository,
)
from nodo.domain.entities import TorrentSearchResult
from nodo.domain.exceptions import (
    AggregatorError,
    AggregatorTimeoutError,
    ValidationError,
)


class SearchTorrents:
    """Use case for searching torrents across multiple aggregators.

    Searches multiple aggregator services, combines results, deduplicates,
    and returns sorted results.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for SearchTorrents use case.

        Attributes:
            query: Search query string.
            aggregator_names: Optional list of aggregator names to search.
                If None, uses favorite aggregators from preferences.
                If provided, must contain at least one aggregator name.
            max_results: Maximum number of results per aggregator.
        """

        query: str
        aggregator_names: list[str] | None = None
        max_results: int = 10

    @dataclass(frozen=True, slots=True, kw_only=True)
    class FailedSearch:
        """DTO for a failed aggregator search.

        Attributes:
            aggregator_name: Name of the aggregator that failed.
            error_message: Error message from the failure.
        """

        aggregator_name: str
        error_message: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for SearchTorrents use case.

        Attributes:
            results: List of search result DTOs.
            failed_searches: List of failed aggregator searches.
        """

        results: tuple[TorrentSearchResultDTO, ...]
        failed_searches: tuple["SearchTorrents.FailedSearch", ...]

    def __init__(
        self,
        aggregator_service_registry: IAggregatorServiceRegistry,
        preferences_repository: IUserPreferencesRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            aggregator_service_registry: Registry for accessing aggregator services.
            preferences_repository: Repository for user preferences.
        """
        self._aggregator_service_registry = aggregator_service_registry
        self._preferences_repository = preferences_repository

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing search criteria.

        Returns:
            Output containing search results.

            Raises:
            ValidationError: If query is empty or invalid.
            AggregatorError: If all aggregators fail or no aggregators available.
            Exception: Any non-AggregatorError/AggregatorTimeoutError exception from
                aggregator services will propagate and fail the use case.
        """
        # Validate query
        if not input_data.query or not input_data.query.strip():
            raise ValidationError("Search query cannot be empty")

        query = input_data.query.strip()

        # Validate max_results
        if input_data.max_results < 1:
            raise ValidationError("max_results must be at least 1")

        # Validate aggregator_names if provided
        if input_data.aggregator_names is not None:
            if len(input_data.aggregator_names) == 0:
                raise ValidationError(
                    "aggregator_names must contain at least one aggregator name"
                )

        # Determine which aggregators to use
        aggregator_names = self._get_aggregator_names(input_data.aggregator_names)

        if not aggregator_names:
            raise AggregatorError("No aggregators available for search")

        # Validate that all provided aggregator names are valid
        if input_data.aggregator_names is not None:
            available_names = set(self._aggregator_service_registry.get_all_names())
            invalid_aggregators = [
                name
                for name in input_data.aggregator_names
                if name not in available_names
            ]
            if invalid_aggregators:
                valid_names = ", ".join(sorted(available_names))
                raise ValidationError(
                    f"Invalid aggregator names: {', '.join(invalid_aggregators)}. "
                    f"Valid aggregators are: {valid_names}"
                )

        # Search each aggregator and collect results
        all_results: list[TorrentSearchResult] = []
        successful_searches = 0
        failed_searches: list[SearchTorrents.FailedSearch] = []

        for aggregator_name in aggregator_names:
            try:
                service = self._aggregator_service_registry.get_service(aggregator_name)

                results = service.search(query, max_results=input_data.max_results)
                all_results.extend(results)

                successful_searches += 1
            except AggregatorTimeoutError as e:
                # Track timeout error
                failed_searches.append(
                    SearchTorrents.FailedSearch(
                        aggregator_name=aggregator_name,
                        error_message=f"Search timed out: {e}",
                    )
                )
                continue
            except AggregatorError as e:
                # Track failed aggregator
                failed_searches.append(
                    SearchTorrents.FailedSearch(
                        aggregator_name=aggregator_name,
                        error_message=f"Search failed: {e}",
                    )
                )
                continue

        # At least one aggregator must succeed
        if successful_searches == 0:
            raise AggregatorError(
                f"All aggregators failed to search for query: {query}"
            )

        # Deduplicate by magnet link using set (keeps first occurrence)
        deduplicated_results = list(set(all_results))

        # Sort by seeders (descending)
        sorted_results = sorted(
            deduplicated_results, key=lambda r: r.seeders, reverse=True
        )

        # Convert to DTOs
        result_dtos = tuple(SearchTorrents._to_dto(result) for result in sorted_results)
        failed_dtos = tuple(failed_searches)

        return SearchTorrents.Output(results=result_dtos, failed_searches=failed_dtos)

    def _get_aggregator_names(self, provided_names: list[str] | None) -> list[str]:
        """Get aggregator names from input or preferences.

        Args:
            provided_names: Optional list of aggregator names from input.
                If None, uses preferences or all available aggregators.
                If provided, must contain at least one name (validated in execute).

        Returns:
            List of aggregator names to search.
        """
        if provided_names is not None:
            return provided_names

        # Get from preferences
        preferences = self._preferences_repository.get()
        favorite_aggregators = preferences.favorite_aggregators

        # If favorites exist, use them; otherwise use all available
        if favorite_aggregators:
            return [str(agg) for agg in favorite_aggregators]

        # Return all available aggregator names
        return self._aggregator_service_registry.get_all_names()

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
