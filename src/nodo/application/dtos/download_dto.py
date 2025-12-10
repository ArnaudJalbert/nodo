"""Download data transfer object."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadDTO:
    """Data transfer object for Download entity.

    Used to transfer download data between layers without exposing
    the domain entity directly.

    Attributes:
        id_: Unique identifier as string.
        magnet_link: The magnet link URI.
        title: Name of the downloaded content.
        file_path: Local file system path.
        source: Which aggregator it was downloaded from.
        status: Current status (DOWNLOADING, COMPLETED, FAILED, PAUSED).
        date_added: When the download was initiated.
        date_completed: When the download finished, None if not completed.
        size: Human-readable size string.
    """

    id_: str
    magnet_link: str
    title: str
    file_path: str
    source: str
    status: str
    date_added: datetime
    date_completed: datetime | None
    size: str
