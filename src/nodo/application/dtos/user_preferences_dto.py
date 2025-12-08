"""User preferences data transfer object."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class UserPreferencesDTO:
    """Data transfer object for UserPreferences entity.

    Used to transfer user preferences data between layers without exposing
    the domain entity directly.

    Attributes:
        id_: Unique identifier as string.
        default_download_path: Default path to save downloads.
        favorite_paths: User's favorite download locations as strings.
        favorite_aggregators: Preferred torrent sources as strings.
        max_concurrent_downloads: Maximum simultaneous downloads.
        auto_start_downloads: Auto-start downloads on add.
        date_created: When preferences were first created.
        date_modified: Last modification time.
    """

    id_: str
    default_download_path: str
    favorite_paths: list[str]
    favorite_aggregators: list[str]
    max_concurrent_downloads: int
    auto_start_downloads: bool
    date_created: datetime
    date_modified: datetime
