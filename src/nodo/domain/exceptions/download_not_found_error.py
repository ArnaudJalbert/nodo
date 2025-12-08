"""Download not found error exception."""

from nodo.domain.exceptions.domain_exception import DomainError


class DownloadNotFoundError(DomainError):
    """Raised when a download cannot be found.

    This exception is raised when attempting to retrieve or operate
    on a download that does not exist in the repository.
    """
