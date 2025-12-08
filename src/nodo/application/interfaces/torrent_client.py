"""Torrent client interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from nodo.domain.value_objects import MagnetLink


@dataclass(frozen=True, slots=True, kw_only=True)
class TorrentStatus:
    """Status information for a torrent in the client.

    Attributes:
        progress: Download progress as percentage (0.0 to 100.0).
        download_rate: Current download speed in bytes per second.
        upload_rate: Current upload speed in bytes per second.
        eta_seconds: Estimated time remaining in seconds, None if unknown.
        is_complete: Whether the download is complete.
        is_paused: Whether the download is paused.
    """

    progress: float
    download_rate: int
    upload_rate: int
    eta_seconds: int | None
    is_complete: bool
    is_paused: bool


class ITorrentClient(ABC):
    """Interface for torrent client operations.

    This abstract base class defines the contract for interacting
    with a torrent client (e.g., qBittorrent, Transmission).
    """

    @abstractmethod
    def add_torrent(self, magnet_link: MagnetLink, download_path: str) -> str:
        """Add a torrent to the client and start downloading.

        Args:
            magnet_link: The magnet link of the torrent.
            download_path: The path where files should be downloaded.

        Returns:
            The torrent hash/ID used by the client.

        Raises:
            TorrentClientError: If adding the torrent fails.
        """

    @abstractmethod
    def get_status(self, torrent_hash: str) -> TorrentStatus | None:
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
