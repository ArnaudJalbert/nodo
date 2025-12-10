"""User preferences repository interface."""

from abc import ABC, abstractmethod

from nodo.domain.entities import UserPreferences


class IUserPreferencesRepository(ABC):
    """Interface for user preferences persistence operations.

    This abstract base class defines the contract for storing and
    retrieving the UserPreferences singleton entity.
    """

    @abstractmethod
    def get(self) -> UserPreferences:
        """Get the user preferences.

        If no preferences exist, creates and returns default preferences.

        Returns:
            The user preferences entity.
        """

    @abstractmethod
    def save(self, preferences: UserPreferences) -> None:
        """Save the user preferences.

        Args:
            preferences: The preferences entity to save.
        """
