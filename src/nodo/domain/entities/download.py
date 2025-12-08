"""Download entity."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from nodo.domain.value_objects import (
    AggregatorSource,
    DownloadStatus,
    FileSize,
    MagnetLink,
)


@dataclass(slots=True, kw_only=True)
class Download:
    """Represents a torrent that has been downloaded or is currently downloading.

    This is the main persisted entity and the source of truth for all
    download tracking.

    Attributes:
        id_: Unique identifier (primary key).
        magnet_link: The magnet link used to download.
        title: Name of the downloaded content.
        file_path: Local file system path where content is saved.
        source: Which aggregator it was downloaded from.
        status: Current status of the download.
        date_added: When the download was initiated.
        date_completed: When the download finished (None if not completed).
        size: Total size of the download.
    """

    magnet_link: MagnetLink
    title: str
    file_path: Path
    source: AggregatorSource
    size: FileSize
    id_: UUID = field(default_factory=uuid4)
    status: DownloadStatus = DownloadStatus.DOWNLOADING
    date_added: datetime = field(default_factory=datetime.now)
    date_completed: datetime | None = None
