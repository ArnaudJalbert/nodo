"""Aggregator timeout error exception."""

from nodo.domain.exceptions.aggregator_error import AggregatorError


class AggregatorTimeoutError(AggregatorError):
    """Raised when aggregator search times out.

    This exception is a specific type of AggregatorError that
    indicates the search operation exceeded the allowed time limit.
    """
