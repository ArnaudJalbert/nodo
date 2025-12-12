"""Add download use case."""

from dataclasses import dataclass
from pathlib import Path

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import IDownloadRepository, ITorrentClient
from nodo.domain.entities import Download
from nodo.domain.exceptions import (
    DuplicateDownloadError,
    TorrentClientError,
    ValidationError,
)
from nodo.domain.value_objects import (
    DownloadState,
    FileSize,
    IndexerSource,
    TorrentLink,
)


class AddDownload:
    """Use case for adding a new download and starting it in the torrent client.

    Creates a Download entity, saves it to the repository, and starts the
    download in the torrent client.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for AddDownload use case.

        Attributes:
            magnet_link: The magnet link URI.
            title: Name of the downloaded content.
            source: Which indexer it was downloaded from.
            size: Human-readable size string (e.g., "1.5 GB").
            file_path: The file path where the download will be stored.
        """

        magnet_link: str
        title: str
        source: str
        size: str
        file_path: str

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for AddDownload use case.

        Attributes:
            download: The created download DTO.
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
            torrent_client: Torrent client for starting downloads.
        """
        self._download_repository = download_repository
        self._torrent_client = torrent_client

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing download information.

        Returns:
            Output containing the created download.

        Raises:
            ValidationError: If input validation fails.
            DuplicateDownloadError: If download with same magnet link exists.
            TorrentClientError: If starting download in client fails.
        """
        # Create value objects with validation
        magnet_link = TorrentLink.from_string(input_data.magnet_link)
        indexer_source = IndexerSource.from_string(input_data.source)
        file_size = FileSize.from_string(input_data.size)
        file_path = Path(input_data.file_path)

        # Validate title
        if not input_data.title or not input_data.title.strip():
            raise ValidationError("Title cannot be empty")

        title = input_data.title.strip()

        # Check for duplicates
        if self._download_repository.exists_by_magnet_link(magnet_link):
            raise DuplicateDownloadError(
                f"Download with link already exists: {magnet_link}"
            )

        # Create Download entity
        download: Download = Download(
            magnet_link=magnet_link,
            title=title,
            file_path=file_path,
            source=indexer_source,
            size=file_size,
        )

        # Save to repository
        self._download_repository.save(download)

        # Start download in torrent client
        try:
            download_dir = str(file_path.parent)
            self._torrent_client.add_torrent(magnet_link, download_dir)
        except TorrentClientError as e:
            # If client fails, update status to FAILED and save
            download.status = DownloadState.FAILED
            self._download_repository.save(download)
            # Re-raise the error so caller knows
            raise TorrentClientError(
                f"Failed to start download in torrent client: {e}"
            ) from e

        # Convert to DTO
        download_dto = AddDownload._to_dto(download)

        return AddDownload.Output(download=download_dto)

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
