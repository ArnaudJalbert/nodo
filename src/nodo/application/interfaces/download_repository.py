"""Download repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from nodo.domain.entities import Download
from nodo.domain.value_objects import DownloadState, MagnetLink


class IDownloadRepository(ABC):
    """Interface for download persistence operations.

    This abstract base class defines the contract for storing and
    retrieving Download entities. Implementations may use SQLite,
    PostgreSQL, or any other storage mechanism.
    """

    @abstractmethod
    def save(self, download: Download) -> None:
        """Save a download to the repository.

        If the download already exists (by id_), it will be updated.
        Otherwise, a new record will be created.

        Args:
            download: The download entity to save.
        """

    @abstractmethod
    def find_by_id(self, id_: UUID) -> Download | None:
        """Find a download by its unique identifier.

        Args:
            id_: The UUID of the download.

        Returns:
            The download if found, None otherwise.
        """

    @abstractmethod
    def find_by_magnet_link(self, magnet_link: MagnetLink) -> Download | None:
        """Find a download by its magnet link.

        Args:
            magnet_link: The magnet link to search for.

        Returns:
            The download if found, None otherwise.
        """

    @abstractmethod
    def find_all(self, status: DownloadState | None = None) -> list[Download]:
        """Find all downloads, optionally filtered by status.

        Args:
            status: Optional status to filter by.

        Returns:
            List of downloads matching the criteria.
        """

    @abstractmethod
    def delete(self, id_: UUID) -> bool:
        """Delete a download by its unique identifier.

        Args:
            id_: The UUID of the download to delete.

        Returns:
            True if the download was deleted, False if not found.
        """

    @abstractmethod
    def exists_by_magnet_link(self, magnet_link: MagnetLink) -> bool:
        """Check if a download with the given magnet link exists.

        Args:
            magnet_link: The magnet link to check.

        Returns:
            True if a download exists, False otherwise.
        """
