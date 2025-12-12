"""Remove favorite indexer use case."""

from dataclasses import dataclass

from nodo.application.interfaces import IUserPreferencesRepository
from nodo.domain.value_objects import IndexerSource


class RemoveFavoriteIndexer:
    """Use case for removing a favorite torrent indexer.

    Removes an indexer from the user's list of favorite torrent sources.
    If the indexer is not in the favorites, no change is made.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for RemoveFavoriteIndexer use case.

        Attributes:
            indexer_name: The name of the indexer to remove from favorites.
        """

        indexer_name: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for RemoveFavoriteIndexer use case.

        Attributes:
            indexer_name: The normalized indexer name.
            removed: Whether the indexer was actually removed (False if not found).
        """

        indexer_name: str
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
            input_data: The input data containing the indexer name to remove.

        Returns:
            Output containing the normalized indexer name and whether it was removed.

        Raises:
            ValidationError: If the indexer name is empty.
            FileSystemError: If there's an error reading or writing preferences.
        """
        source = IndexerSource.from_string(input_data.indexer_name)
        preferences = self._preferences_repository.get()
        count_before = len(preferences.favorite_indexers)
        preferences.remove_favorite_indexer(source)
        removed = len(preferences.favorite_indexers) < count_before
        self._preferences_repository.save(preferences)
        return RemoveFavoriteIndexer.Output(
            indexer_name=str(source),
            removed=removed,
        )
