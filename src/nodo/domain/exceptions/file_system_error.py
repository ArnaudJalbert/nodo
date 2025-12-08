"""File system error exception."""

from nodo.domain.exceptions.domain_exception import DomainException


class FileSystemError(DomainException):
    """Raised when file system operations fail.

    This exception is raised when file system operations such as
    creating directories, checking permissions, or accessing paths
    encounter errors.
    """
