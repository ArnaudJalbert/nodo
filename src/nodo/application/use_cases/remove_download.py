"""Remove download use case."""

from dataclasses import dataclass
from uuid import UUID

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import (
    IDownloadRepository,
    IFileSystemRepository,
    ITorrentClient,
)
from nodo.domain.entities import Download
from nodo.domain.exceptions import (
    DownloadNotFoundError,
    TorrentClientError,
    ValidationError,
)


class RemoveDownload:
    """Use case for removing a download from tracking.

    Removes the download from the torrent client and optionally deletes
    the downloaded files, then removes it from the repository.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for RemoveDownload use case.

        Attributes:
            download_id: The UUID of the download as a string.
            delete_files: Whether to delete downloaded files (default: False).
        """

        download_id: str
        delete_files: bool = False

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for RemoveDownload use case.

        Attributes:
            download: The removed download DTO.
            removed: Whether the download was actually removed.
        """

        download: DownloadDTO
        removed: bool

    def __init__(
        self,
        download_repository: IDownloadRepository,
        torrent_client: ITorrentClient,
        file_system_repository: IFileSystemRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            download_repository: Repository for download persistence.
            torrent_client: Torrent client for removing downloads.
            file_system_repository: Repository for file system operations.
        """
        self._download_repository = download_repository
        self._torrent_client = torrent_client
        self._file_system_repository = file_system_repository

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing the download ID and delete option.

        Returns:
            Output containing the removed download and removal status.

        Raises:
            ValidationError: If download_id is not a valid UUID.
            DownloadNotFoundError: If download with given ID not found.
            TorrentClientError: If removing from torrent client fails.
        """
        # Validate UUID format
        try:
            download_uuid = UUID(input_data.download_id)
        except ValueError as e:
            raise ValidationError(
                f"Invalid download ID format: {input_data.download_id}"
            ) from e

        # Retrieve download from the repository
        download = self._download_repository.find_by_id(download_uuid)
        if download is None:
            raise DownloadNotFoundError(f"Download not found: {input_data.download_id}")

        # Extract torrent hash from the magnet link
        torrent_hash = download.magnet_link.info_hash

        # Remove from the torrent client
        try:
            client_removed = self._torrent_client.remove(
                torrent_hash, delete_files=input_data.delete_files
            )
        except TorrentClientError as e:
            raise TorrentClientError(
                f"Failed to remove download from torrent client: {e}"
            ) from e

        # Delete files if requested and the client didn't handle it
        if input_data.delete_files and not client_removed:
            # Client didn't remove it, so we need to delete files manually
            self._file_system_repository.delete_path(download.file_path)

        # Remove from repository
        removed = self._download_repository.delete(download_uuid)

        # Convert to DTO
        download_dto = RemoveDownload._to_dto(download)

        return RemoveDownload.Output(download=download_dto, removed=removed)

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
