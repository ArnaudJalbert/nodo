"""Torrent client error exception."""

from nodo.domain.exceptions.domain_exception import DomainException


class TorrentClientError(DomainException):
    """Raised when torrent client operations fail.

    This exception is raised when communication with the torrent
    client (e.g., qBittorrent) fails or returns an error.
    """
