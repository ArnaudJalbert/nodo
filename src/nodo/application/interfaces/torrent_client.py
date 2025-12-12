"""Torrent client interface."""

from abc import ABC, abstractmethod

from nodo.domain.entities import DownloadStatus
from nodo.domain.value_objects import TorrentLink


class ITorrentClient(ABC):
    """Interface for torrent client operations.

    This abstract base class defines the contract for interacting
    with a torrent client (e.g., qBittorrent, Transmission).
    """

    @abstractmethod
    def add_torrent(self, magnet_link: TorrentLink, download_path: str) -> str:
        """Add a torrent to the client and start downloading.

        Args:
            magnet_link: The torrent link (magnet URI or HTTP/HTTPS URL).
            download_path: The path where files should be downloaded.

        Returns:
            The torrent hash/ID used by the client.

        Raises:
            TorrentClientError: If adding the torrent fails.
        """

    @abstractmethod
    def get_status(self, torrent_hash: str) -> DownloadStatus | None:
        """Get the current status of a torrent.

        Args:
            torrent_hash: The torrent hash/ID.

        Returns:
            The torrent status, or None if not found.

        Raises:
            TorrentClientError: If getting status fails.
        """

    @abstractmethod
    def pause(self, torrent_hash: str) -> bool:
        """Pause a torrent.

        Args:
            torrent_hash: The torrent hash/ID.

        Returns:
            True if paused successfully, False if not found.

        Raises:
            TorrentClientError: If pausing fails.
        """

    @abstractmethod
    def resume(self, torrent_hash: str) -> bool:
        """Resume a paused torrent.

        Args:
            torrent_hash: The torrent hash/ID.

        Returns:
            True if resumed successfully, False if not found.

        Raises:
            TorrentClientError: If resuming fails.
        """

    @abstractmethod
    def remove(self, torrent_hash: str, delete_files: bool = False) -> bool:
        """Remove a torrent from the client.

        Args:
            torrent_hash: The torrent hash/ID.
            delete_files: Whether to also delete downloaded files.

        Returns:
            True if removed successfully, False if not found.

        Raises:
            TorrentClientError: If removal fails.
        """
