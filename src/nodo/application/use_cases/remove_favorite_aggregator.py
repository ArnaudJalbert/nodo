"""Remove favorite aggregator use case."""

from dataclasses import dataclass

from nodo.application.interfaces import IUserPreferencesRepository
from nodo.domain.value_objects import AggregatorSource


class RemoveFavoriteAggregator:
    """Use case for removing a favorite torrent aggregator.

    Removes an aggregator from the user's list of favorite torrent sources.
    If the aggregator is not in the favorites, no change is made.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for RemoveFavoriteAggregator use case.

        Attributes:
            aggregator_name: The name of the aggregator to remove from favorites.
        """

        aggregator_name: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for RemoveFavoriteAggregator use case.

        Attributes:
            aggregator_name: The normalized aggregator name.
            removed: Whether the aggregator was actually removed (False if not found).
        """

        aggregator_name: str
        removed: bool

    def __init__(self, preferences_repository: IUserPreferencesRepository) -> None:
        """Initialize the use case.

        Args:
            preferences_repository: Repository for user preferences persistence.
        """
        self._preferences_repository = preferences_repository

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing the aggregator name to remove.

        Returns:
            Output containing the normalized aggregator name and whether it was removed.

        Raises:
            ValidationError: If the aggregator name is empty.
            FileSystemError: If there's an error reading or writing preferences.
        """
        source = AggregatorSource.from_string(input_data.aggregator_name)
        preferences = self._preferences_repository.get()
        count_before = len(preferences.favorite_aggregators)
        preferences.remove_favorite_aggregator(source)
        removed = len(preferences.favorite_aggregators) < count_before
        self._preferences_repository.save(preferences)
        return RemoveFavoriteAggregator.Output(
            aggregator_name=str(source),
            removed=removed,
        )
