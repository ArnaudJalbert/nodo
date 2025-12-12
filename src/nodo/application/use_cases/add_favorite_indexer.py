"""Add a favorite indexer use case."""

from dataclasses import dataclass

from nodo.application.interfaces import IUserPreferencesRepository
from nodo.domain import ValidationError
from nodo.domain.value_objects import IndexerSource


class AddFavoriteIndexer:
    """Use case for adding a favorite torrent indexer.

    Adds an indexer to the user's list of favorite torrent sources.
    If the indexer is already in the favorites, no change is made.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for the AddFavoriteIndexer use case.

        Attributes:
            indexer_name: The name of the indexer to add to favorites.
        """

        indexer_name: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for AddFavoriteIndexer use case.

        Attributes:
            indexer_name: The normalized indexer name.
            added: Whether the indexer was actually added (False if already existed).
        """

        indexer_name: str
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
            input_data: The input data containing the indexer name to add.

        Returns:
            Output containing the normalized indexer name and whether it was added.

        Raises:
            ValidationError: If the indexer name is empty or
                             not a supported indexer.
            FileSystemError: If there's an error reading or writing preferences.
        """
        source = IndexerSource.from_string(input_data.indexer_name)
        if not source.is_supported:
            raise ValidationError(
                f"Unsupported indexer: '{input_data.indexer_name}'. "
                f"Supported indexers: {
                    ', '.join(IndexerSource.get_supported_indexers())
                }"
            )
        preferences = self._preferences_repository.get()
        count_before = len(preferences.favorite_indexers)
        preferences.add_favorite_indexer(source)
        added = len(preferences.favorite_indexers) > count_before
        self._preferences_repository.save(preferences)
        return AddFavoriteIndexer.Output(
            indexer_name=str(source),
            added=added,
        )
