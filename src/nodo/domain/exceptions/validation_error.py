"""Validation error exception."""

from nodo.domain.exceptions.domain_exception import DomainException


class ValidationError(DomainException):
    """Raised when input validation fails.

    This exception is raised when data does not meet the required
    validation rules, such as invalid formats, out-of-range values,
    or missing required fields.
    """
