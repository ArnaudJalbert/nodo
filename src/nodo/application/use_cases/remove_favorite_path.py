"""Remove favorite path use case."""

from dataclasses import dataclass
from pathlib import Path

from nodo.application.interfaces import IUserPreferencesRepository


class RemoveFavoritePath:
    """Use case for removing a favorite download location.

    Removes a path from the user's list of favorite download locations.
    If the path is not in the favorites, no change is made.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for RemoveFavoritePath use case.

        Attributes:
            path: The path to remove from favorites.
        """

        path: Path

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for RemoveFavoritePath use case.

        Attributes:
            path: The path that was requested to be removed.
            removed: Whether the path was actually removed (False if not found).
        """

        path: str
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
            input_data: The input data containing the path to remove.

        Returns:
            Output containing the path and whether it was removed.

        Raises:
            FileSystemError: If there's an error reading or writing preferences.
        """
        preferences = self._preferences_repository.get()
        count_before = len(preferences.favorite_paths)
        preferences.remove_favorite_path(input_data.path)
        removed = len(preferences.favorite_paths) < count_before
        self._preferences_repository.save(preferences)
        return RemoveFavoritePath.Output(
            path=str(input_data.path),
            removed=removed,
        )
