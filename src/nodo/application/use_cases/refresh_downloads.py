"""Refresh downloads use case."""

from dataclasses import dataclass
from datetime import datetime

from nodo.application.interfaces import IDownloadRepository, ITorrentClient
from nodo.domain.entities import Download
from nodo.domain.value_objects import DownloadState


class RefreshDownloads:
    """Use case for refreshing download statuses with torrent client.

    Syncs download statuses with the torrent client by querying each
    active download and updating its status if it has changed.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for RefreshDownloads use case.

        Attributes:
            None - No input required, refreshes all active downloads.
        """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for RefreshDownloads use case.

        Attributes:
            updated_count: Number of downloads that were updated.
            error_count: Number of errors encountered during refresh.
            errors: List of error messages encountered.
        """

        updated_count: int
        error_count: int
        errors: tuple[str, ...]

    # Mapping of (is_complete, is_paused) tuples to DownloadState
    _STATUS_MAPPER: dict[tuple[bool, bool], DownloadState] = {
        (True, False): DownloadState.COMPLETED,
        (True, True): DownloadState.COMPLETED,  # Complete takes precedence
        (False, True): DownloadState.PAUSED,
        (False, False): DownloadState.DOWNLOADING,
    }

    def __init__(
        self,
        download_repository: IDownloadRepository,
        torrent_client: ITorrentClient,
    ) -> None:
        """Initialize the use case.

        Args:
            download_repository: Repository for download persistence.
            torrent_client: Torrent client for querying status.
        """
        self._download_repository = download_repository
        self._torrent_client = torrent_client

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data (no input required).

        Returns:
            Output containing counts of updated downloads and errors.

        Note:
            This use case catches errors for individual downloads and continues
            processing. Only critical repository failures would cause it to raise.
        """
        # Get all active downloads (DOWNLOADING or PAUSED)
        active_downloads = self._download_repository.find_all(
            status=DownloadState.DOWNLOADING
        ) + self._download_repository.find_all(status=DownloadState.PAUSED)

        updated_count = 0
        errors: list[str] = []

        for download in active_downloads:
            try:
                updated = self._refresh_single_download(download)
                if updated:
                    updated_count += 1
            except Exception as e:
                # Record error but continue processing other downloads
                error_msg = (
                    f"Failed to refresh download {download.id_}: "
                    f"{type(e).__name__}: {e}"
                )
                errors.append(error_msg)

        return RefreshDownloads.Output(
            updated_count=updated_count,
            error_count=len(errors),
            errors=tuple(errors),
        )

    def _refresh_single_download(self, download: Download) -> bool:
        """Refresh a single download's status.

        Args:
            download: The download entity to refresh.

        Returns:
            True if the download was updated, False otherwise.

        Raises:
            TorrentClientError: If querying torrent client fails (caught by caller).
        """
        torrent_hash = download.magnet_link.info_hash

        # Query torrent client for status
        torrent_status = self._torrent_client.get_status(torrent_hash)

        # If torrent not found in client, skip (might have been removed externally)
        if torrent_status is None:
            return False

        # Determine new status based on torrent client status
        status_key = (torrent_status.is_complete, torrent_status.is_paused)
        new_status = self._STATUS_MAPPER[status_key]

        # Update status if changed
        updated = False
        if download.status != new_status:
            download.status = new_status

            # Set date_completed if newly completed
            if (
                new_status == DownloadState.COMPLETED
                and download.date_completed is None
            ):
                download.date_completed = datetime.now()

            # Save updated entity
            self._download_repository.save(download)
            updated = True

        return updated
