"""File system repository interface."""

from abc import ABC, abstractmethod
from pathlib import Path


class IFileSystemRepository(ABC):
    """Interface for file system operations.

    This abstract base class defines the contract for file system operations
    like deleting files and directories. Implementations may use different
    strategies for file system access.
    """

    @abstractmethod
    def delete_path(self, path: Path) -> None:
        """Delete a file or directory.

        Args:
            path: The path to the file or directory to delete.

        Raises:
            FileSystemError: If deletion fails.
        """
