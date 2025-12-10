"""Get download status use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import (
    IDownloadRepository,
    ITorrentClient,
)
from nodo.domain.entities import Download, DownloadStatus
from nodo.domain.exceptions import (
    DownloadNotFoundError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import DownloadState, FileSize, TimeDuration


class GetDownloadStatus:
    """Use case for getting the current status and progress of a download.

    Retrieves the download from the repository, queries the torrent client
    for current status, updates the download entity if status changed,
    and returns the download with progress information.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for GetDownloadStatus use case.

        Attributes:
            download_id: The UUID of the download as a string.
        """

        download_id: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for GetDownloadStatus use case.

        Attributes:
            download: The download DTO with current status.
            progress: Download progress as percentage (0.0 to 100.0).
            download_rate: Current download speed in human-readable format,
                or None if not readable.
            upload_rate: Current upload speed in human-readable format,
                or None if not readable.
            eta: Estimated time remaining in human-readable format,
                or None if not readable.
        """

        download: DownloadDTO
        progress: float
        download_rate: str | None
        upload_rate: str | None
        eta: str | None

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
            input_data: The input data containing the download ID.

        Returns:
            Output containing the download and progress information.

        Raises:
            ValidationError: If download_id is not a valid UUID.
            DownloadNotFoundError: If download with given ID not found.
            TorrentClientError: If querying torrent client fails.
        """
        # Validate UUID format
        try:
            download_uuid = UUID(input_data.download_id)
        except ValueError as e:
            raise ValidationError(
                f"Invalid download ID format: {input_data.download_id}"
            ) from e

        # Retrieve download from repository
        download = self._download_repository.find_by_id(download_uuid)
        if download is None:
            raise DownloadNotFoundError(f"Download not found: {input_data.download_id}")

        # Extract torrent hash from magnet link
        torrent_hash = download.magnet_link.info_hash

        # Query torrent client for status
        try:
            torrent_status = self._torrent_client.get_status(torrent_hash)
        except TorrentClientError as e:
            raise TorrentClientError(
                f"Failed to get status from torrent client: {e}"
            ) from e

        # Update download entity if status changed
        if torrent_status is not None:
            download = self._update_download_status(download, torrent_status)
            self._download_repository.save(download)

        # Convert to DTO
        download_dto = GetDownloadStatus._to_dto(download)

        # Format progress information
        if torrent_status is None:
            # Torrent not found in client - return current entity status
            progress = 0.0
            download_rate = None
            upload_rate = None
            eta = None
        else:
            progress = torrent_status.progress
            download_rate = GetDownloadStatus._format_speed(
                torrent_status.download_rate
            )
            upload_rate = GetDownloadStatus._format_speed(torrent_status.upload_rate)
            eta = GetDownloadStatus._format_eta(torrent_status.eta_seconds)

        return GetDownloadStatus.Output(
            download=download_dto,
            progress=progress,
            download_rate=download_rate,
            upload_rate=upload_rate,
            eta=eta,
        )

    # Mapping of (is_complete, is_paused) tuples to DownloadState
    _STATUS_MAPPER: dict[tuple[bool, bool], DownloadState] = {
        (True, False): DownloadState.COMPLETED,
        (True, True): DownloadState.COMPLETED,  # Complete takes precedence
        (False, True): DownloadState.PAUSED,
        (False, False): DownloadState.DOWNLOADING,
    }

    def _update_download_status(
        self, download: Download, torrent_status: DownloadStatus
    ) -> Download:
        """Update download status based on torrent client status.

        Args:
            download: The download entity to update.
            torrent_status: The current status from torrent client.

        Returns:
            Updated download entity.
        """
        # Determine new status based on torrent client status
        status_key = (torrent_status.is_complete, torrent_status.is_paused)
        new_status = self._STATUS_MAPPER[status_key]

        # Update status if changed
        if download.status != new_status:
            download.status = new_status

            # Set date_completed if newly completed
            if (
                new_status == DownloadState.COMPLETED
                and download.date_completed is None
            ):
                download.date_completed = datetime.now()

        return download

    @staticmethod
    def _format_speed(bytes_per_second: int) -> str | None:
        """Format bytes per second to human-readable speed string.

        Args:
            bytes_per_second: Speed in bytes per second.

        Returns:
            Human-readable speed string (e.g., "1.5 MB/s"), or None if not readable.
        """
        # Validate: must be non-negative and reasonable (not too large)
        # Max reasonable: 1 PB/s (1024^5 bytes/s)
        max_reasonable = 1024**5
        if bytes_per_second < 0 or bytes_per_second > max_reasonable:
            return None

        if bytes_per_second == 0:
            return "0 B/s"

        try:
            size = FileSize.from_bytes(bytes_per_second)
            return f"{size}/s"
        except ValidationError:
            # If FileSize validation fails, return None
            return None

    @staticmethod
    def _format_eta(eta_seconds: int | None) -> str | None:
        """Format ETA seconds to human-readable time string.

        Args:
            eta_seconds: Estimated time remaining in seconds, or None if unknown.

        Returns:
            Human-readable time string (e.g., "5 minutes"), or None if not readable.
        """
        try:
            duration = TimeDuration.from_seconds(eta_seconds)
            if duration is None:
                return None
            return duration.to_human_readable()
        except ValidationError:
            # If validation fails (negative or too large), return None
            return None

    @staticmethod
    def _to_dto(download: Download) -> DownloadDTO:
        """Convert Download entity to DownloadDTO.

        Args:
            download: The download entity to convert.

        Returns:
            DownloadDTO representation of the entity.
        """
        return DownloadDTO(
            id_=str(download.id_),
            magnet_link=str(download.magnet_link),
            title=download.title,
            file_path=str(download.file_path),
            source=str(download.source),
            status=download.status.name,
            date_added=download.date_added,
            date_completed=download.date_completed,
            size=str(download.size),
        )
