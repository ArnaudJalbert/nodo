"""Update user preferences use case."""

from dataclasses import dataclass
from pathlib import Path

from nodo.application.interfaces import IUserPreferencesRepository


class UpdateUserPreferences:
    """Use case for updating user preference settings.

    Allows updating the default download path, max concurrent downloads,
    and auto-start downloads setting.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for UpdateUserPreferences use case.

        Attributes:
            default_download_path: New default download path (optional).
            max_concurrent_downloads: New max concurrent downloads (optional).
            auto_start_downloads: New auto-start setting (optional).
        """

        default_download_path: Path | None = None
        max_concurrent_downloads: int | None = None
        auto_start_downloads: bool | None = None

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for UpdateUserPreferences use case.

        Attributes:
            default_download_path: Updated default download path (if changed).
            max_concurrent_downloads: Updated max concurrent downloads (if changed).
            auto_start_downloads: Updated auto-start setting (if changed).
        """

        default_download_path: str | None = None
        max_concurrent_downloads: int | None = None
        auto_start_downloads: bool | None = None

    def __init__(self, preferences_repository: IUserPreferencesRepository) -> None:
        """Initialize the use case.

        Args:
            preferences_repository: Repository for user preferences persistence.
        """
        self._preferences_repository = preferences_repository

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing optional preference updates.

        Returns:
            Output containing only the fields that were updated.

        Raises:
            ValidationError: If max_concurrent_downloads is not between 1 and 10.
            FileSystemError: If there's an error reading or writing preferences.
        """
        preferences = self._preferences_repository.get()

        updated_path: str | None = None
        updated_max: int | None = None
        updated_auto: bool | None = None

        if input_data.default_download_path is not None:
            preferences.update_default_path(input_data.default_download_path)
            updated_path = str(preferences.default_download_path)

        if input_data.max_concurrent_downloads is not None:
            preferences.update_max_concurrent_downloads(
                input_data.max_concurrent_downloads
            )
            updated_max = preferences.max_concurrent_downloads

        if input_data.auto_start_downloads is not None:
            preferences.update_auto_start(input_data.auto_start_downloads)
            updated_auto = preferences.auto_start_downloads

        self._preferences_repository.save(preferences)
        return UpdateUserPreferences.Output(
            default_download_path=updated_path,
            max_concurrent_downloads=updated_max,
            auto_start_downloads=updated_auto,
        )
