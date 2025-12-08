"""Duplicate download error exception."""

from nodo.domain.exceptions.domain_exception import DomainException


class DuplicateDownloadError(DomainException):
    """Raised when attempting to add a duplicate download.

    This exception is raised when trying to add a download with a
    magnet link that already exists in the repository.
    """
