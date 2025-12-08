"""Base domain exception."""


class DomainError(Exception):
    """Base exception for all domain errors.

    All domain-specific exceptions should inherit from this class
    to allow for consistent error handling across the application.
    """
