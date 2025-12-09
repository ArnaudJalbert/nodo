"""Get user preferences use case."""

from dataclasses import dataclass
from datetime import datetime

from nodo.application.interfaces import IUserPreferencesRepository


class GetUserPreferences:
    """Use case for retrieving user preferences.

    Loads the user preferences from the repository and returns them as output data.
    If no preferences exist, the repository will create and return default preferences.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for GetUserPreferences use case.

        Attributes:
            id_: Unique identifier as string.
            default_download_path: Default path to save downloads.
            favorite_paths: User's favorite download locations as strings.
            favorite_aggregators: Preferred torrent sources as strings.
            max_concurrent_downloads: Maximum simultaneous downloads.
            auto_start_downloads: Auto-start downloads on add.
            date_created: When preferences were first created.
            date_modified: Last modification time.
        """

        id_: str
        default_download_path: str
        favorite_paths: tuple[str, ...]
        favorite_aggregators: tuple[str, ...]
        max_concurrent_downloads: int
        auto_start_downloads: bool
        date_created: datetime
        date_modified: datetime

    def __init__(self, preferences_repository: IUserPreferencesRepository) -> None:
        """Initialize the use case.

        Args:
            preferences_repository: Repository for user preferences persistence.
        """
        self._preferences_repository = preferences_repository

    def execute(self) -> Output:
        """Execute the use case.

        Returns:
            Output containing the current user preferences.

        Raises:
            FileSystemError: If there's an error reading preferences from storage.
        """
        preferences = self._preferences_repository.get()
        return GetUserPreferences.Output(
            id_=str(preferences.id_),
            default_download_path=str(preferences.default_download_path),
            favorite_paths=tuple(str(path) for path in preferences.favorite_paths),
            favorite_aggregators=tuple(
                str(source) for source in preferences.favorite_aggregators
            ),
            max_concurrent_downloads=preferences.max_concurrent_downloads,
            auto_start_downloads=preferences.auto_start_downloads,
            date_created=preferences.date_created,
            date_modified=preferences.date_modified,
        )
