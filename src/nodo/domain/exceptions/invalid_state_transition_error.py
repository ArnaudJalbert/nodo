"""Invalid state transition error exception."""

from nodo.domain.exceptions.domain_exception import DomainException


class InvalidStateTransitionError(DomainException):
    """Raised when attempting an invalid status change.

    This exception is raised when trying to transition a download
    to a state that is not valid from its current state, such as
    resuming a download that is not paused.
    """
