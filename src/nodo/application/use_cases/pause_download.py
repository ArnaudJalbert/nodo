"""Pause download use case."""

from dataclasses import dataclass
from uuid import UUID

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import IDownloadRepository, ITorrentClient
from nodo.domain.entities import Download
from nodo.domain.exceptions import (
    DownloadNotFoundError,
    InvalidStateTransitionError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import DownloadState


class PauseDownload:
    """Use case for pausing an active download.

    Pauses the download in the torrent client and updates the download
    entity status to PAUSED.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for PauseDownload use case.

        Attributes:
            download_id: The UUID of the download as a string.
        """

        download_id: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for PauseDownload use case.

        Attributes:
            download: The paused download DTO.
        """

        download: DownloadDTO

    def __init__(
        self,
        download_repository: IDownloadRepository,
        torrent_client: ITorrentClient,
    ) -> None:
        """Initialize the use case.

        Args:
            download_repository: Repository for download persistence.
            torrent_client: Torrent client for pausing downloads.
        """
        self._download_repository = download_repository
        self._torrent_client = torrent_client

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing the download ID.

        Returns:
            Output containing the paused download.

        Raises:
            ValidationError: If download_id is not a valid UUID.
            DownloadNotFoundError: If download with given ID not found.
            InvalidStateTransitionError: If download cannot be paused from
                current status.
            TorrentClientError: If pausing in torrent client fails.
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

        # Verify status allows pausing
        if download.status != DownloadState.DOWNLOADING:
            raise InvalidStateTransitionError(
                f"Cannot pause download with status {download.status.name}. "
                f"Only downloads with status DOWNLOADING can be paused."
            )

        # Extract torrent hash from magnet link
        torrent_hash = download.magnet_link.info_hash

        # Pause in torrent client
        try:
            paused = self._torrent_client.pause(torrent_hash)
            if not paused:
                raise TorrentClientError(f"Torrent not found in client: {torrent_hash}")
        except TorrentClientError as e:
            raise TorrentClientError(
                f"Failed to pause download in torrent client: {e}"
            ) from e

        # Update entity status to PAUSED
        download.status = DownloadState.PAUSED
        self._download_repository.save(download)

        # Convert to DTO
        download_dto = PauseDownload._to_dto(download)

        return PauseDownload.Output(download=download_dto)

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
