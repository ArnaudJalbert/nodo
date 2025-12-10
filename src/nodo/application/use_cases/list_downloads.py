"""List downloads use case."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from nodo.application.dtos import DownloadDTO
from nodo.application.interfaces import IDownloadRepository
from nodo.domain.entities import Download
from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import DownloadState


class ListDownloads:
    """Use case for listing downloads with optional filtering and sorting.

    Retrieves downloads from the repository, optionally filtered by status,
    and returns them sorted according to the specified criteria.
    """

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Input:
        """Input data for ListDownloads use case.

        Attributes:
            status: Optional status to filter by
                (DOWNLOADING, COMPLETED, FAILED, PAUSED).
            sort_by: Field to sort by (default: "date_added").
            ascending: Whether to sort in ascending order (default: False).
        """

        status: str | None = None
        sort_by: str = "date_added"
        ascending: bool = False

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Output:
        """Output data for ListDownloads use case.

        Attributes:
            downloads: List of download DTOs.
        """

        downloads: tuple[DownloadDTO, ...]

    # Mapping of sort fields to their key extraction functions
    _SORT_KEY_MAPPERS: dict[str, Callable[[Download], str | int | datetime]] = {
        "id_": lambda d: str(d.id_),
        "title": lambda d: d.title.lower(),
        "date_added": lambda d: d.date_added,
        "date_completed": lambda d: (
            d.date_completed if d.date_completed else datetime.min
        ),
        "status": lambda d: d.status.name,
        "source": lambda d: str(d.source).lower(),
        "size": lambda d: d.size.bytes_,
    }

    # Valid sort fields derived from mapper keys
    _VALID_SORT_FIELDS = set(_SORT_KEY_MAPPERS.keys())

    def __init__(self, download_repository: IDownloadRepository) -> None:
        """Initialize the use case.

        Args:
            download_repository: Repository for download persistence.
        """
        self._download_repository = download_repository

    def execute(self, input_data: Input) -> Output:
        """Execute the use case.

        Args:
            input_data: The input data containing filter and sort criteria.

        Returns:
            Output containing the list of downloads.

        Raises:
            ValidationError: If status is invalid or sort_by field is invalid.
        """
        # Convert status string to enum if provided
        status_filter: DownloadState | None = None
        if input_data.status is not None:
            try:
                status_filter = DownloadState[input_data.status.upper()]
            except KeyError:
                valid_statuses = [s.name for s in DownloadState]
                raise ValidationError(
                    f"Invalid status '{input_data.status}'. "
                    f"Must be one of: {', '.join(valid_statuses)}"
                )

        # Validate sort_by field
        if input_data.sort_by not in self._VALID_SORT_FIELDS:
            valid_fields = ", ".join(sorted(self._VALID_SORT_FIELDS))
            raise ValidationError(
                f"Invalid sort_by field '{input_data.sort_by}'. "
                f"Must be one of: {valid_fields}"
            )

        # Query repository
        downloads = self._download_repository.find_all(status=status_filter)

        # Sort downloads
        sorted_downloads = ListDownloads._sort_downloads(
            downloads, input_data.sort_by, input_data.ascending
        )

        # Convert to DTOs
        download_dtos = tuple(
            ListDownloads._to_dto(download) for download in sorted_downloads
        )

        return ListDownloads.Output(downloads=download_dtos)

    @staticmethod
    def _sort_downloads(
        downloads: list[Download], sort_by: str, ascending: bool
    ) -> list[Download]:
        """Sort downloads by the specified field.

        Args:
            downloads: List of downloads to sort.
            sort_by: Field name to sort by.
            ascending: Whether to sort in ascending order.

        Returns:
            Sorted list of downloads.

        Raises:
            ValidationError: If sort_by field is not supported.
        """
        if sort_by not in ListDownloads._SORT_KEY_MAPPERS:
            valid_fields = ", ".join(sorted(ListDownloads._VALID_SORT_FIELDS))
            raise ValidationError(
                f"Unsupported sort_by field '{sort_by}'. Must be one of: {valid_fields}"
            )

        key_func = ListDownloads._SORT_KEY_MAPPERS[sort_by]
        reverse = not ascending
        return sorted(downloads, key=key_func, reverse=reverse)

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
