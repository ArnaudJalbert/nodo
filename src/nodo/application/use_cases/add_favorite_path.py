"""Add favorite path use case."""

from dataclasses import dataclass
from pathlib import Path

from nodo.application.interfaces import IUserPreferencesRepository


class AddFavoritePath:
    """Use case for adding a favorite download location.

    Adds a path to the user's list of favorite download locations.
    If the path is already in the favorites, no change is made.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for AddFavoritePath use case.

        Attributes:
            path: The path to add to favorites.
        """

        path: Path

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for AddFavoritePath use case.

        Attributes:
            path: The path that was added.
            added: Whether the path was actually added (False if already existed).
        """

        path: str
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
            input_data: The input data containing the path to add.

        Returns:
            Output containing the path and whether it was added.

        Raises:
            FileSystemError: If there's an error reading or writing preferences.
        """
        preferences = self._preferences_repository.get()
        count_before = len(preferences.favorite_paths)
        preferences.add_favorite_path(input_data.path)
        added = len(preferences.favorite_paths) > count_before
        self._preferences_repository.save(preferences)
        return AddFavoritePath.Output(
            path=str(input_data.path),
            added=added,
        )
