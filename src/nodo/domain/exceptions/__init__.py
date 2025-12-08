"""Domain exceptions for the Nodo application."""

from nodo.domain.exceptions.aggregator_error import AggregatorError
from nodo.domain.exceptions.aggregator_timeout_error import AggregatorTimeoutError
from nodo.domain.exceptions.domain_exception import DomainException
from nodo.domain.exceptions.download_not_found_error import DownloadNotFoundError
from nodo.domain.exceptions.duplicate_download_error import DuplicateDownloadError
from nodo.domain.exceptions.file_system_error import FileSystemError
from nodo.domain.exceptions.invalid_state_transition_error import (
    InvalidStateTransitionError,
)
from nodo.domain.exceptions.torrent_client_error import TorrentClientError
from nodo.domain.exceptions.validation_error import ValidationError

__all__ = [
    "AggregatorError",
    "AggregatorTimeoutError",
    "DomainException",
    "DownloadNotFoundError",
    "DuplicateDownloadError",
    "FileSystemError",
    "InvalidStateTransitionError",
    "TorrentClientError",
    "ValidationError",
]
