"""Aggregator error exception."""

from nodo.domain.exceptions.domain_exception import DomainError


class AggregatorError(DomainError):
    """Raised when aggregator search fails.

    This exception is raised when searching torrent aggregators
    encounters an error, such as connection failures or invalid
    responses.
    """
