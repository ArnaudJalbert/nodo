"""Indexer error exception."""

from nodo.domain.exceptions.domain_exception import DomainError


class IndexerError(DomainError):
    """Raised when indexer search fails.

    This exception is raised when searching torrent indexers
    encounters an error, such as connection failures or invalid
    responses.
    """


class IndexerTimeoutError(IndexerError):
    """Raised when an indexer search times out.

    This exception is raised when a search request to an indexer
    takes longer than the configured timeout.
    """
