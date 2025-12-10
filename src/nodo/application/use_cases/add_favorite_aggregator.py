"""Add favorite aggregator use case."""

from dataclasses import dataclass

from nodo.application.interfaces import IUserPreferencesRepository
from nodo.domain import ValidationError
from nodo.domain.value_objects import AggregatorSource


class AddFavoriteAggregator:
    """Use case for adding a favorite torrent aggregator.

    Adds an aggregator to the user's list of favorite torrent sources.
    If the aggregator is already in the favorites, no change is made.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for AddFavoriteAggregator use case.

        Attributes:
            aggregator_name: The name of the aggregator to add to favorites.
        """

        aggregator_name: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for AddFavoriteAggregator use case.

        Attributes:
            aggregator_name: The normalized aggregator name.
            added: Whether the aggregator was actually added (False if already existed).
        """

        aggregator_name: str
        added: bool

    def __init__(self, preferences_repository: IUserPreferencesRepository) -> None:
        """Initialize the use case.

        Args:
            preferences_repository: Repository for user preferences persistence.
        """
        self._preferences_repository = preferences_repository

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing the aggregator name to add.

        Returns:
            Output containing the normalized aggregator name and whether it was added.

        Raises:
            ValidationError: If the aggregator name is empty or not a supported aggregator.
            FileSystemError: If there's an error reading or writing preferences.
        """
        source = AggregatorSource.from_string(input_data.aggregator_name)
        if not source.is_supported:
            raise ValidationError(
                f"Unsupported aggregator: '{input_data.aggregator_name}'. "
                f"Supported aggregators: {', '.join(AggregatorSource.get_supported_aggregators())}"
            )
        preferences = self._preferences_repository.get()
        count_before = len(preferences.favorite_aggregators)
        preferences.add_favorite_aggregator(source)
        added = len(preferences.favorite_aggregators) > count_before
        self._preferences_repository.save(preferences)
        return AddFavoriteAggregator.Output(
            aggregator_name=str(source),
            added=added,
        )
