"""User preferences entity."""

from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar
from uuid import UUID

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import AggregatorSource

# Well-known singleton UUID for UserPreferences
USER_PREFERENCES_ID = UUID("00000000-0000-0000-0000-000000000001")

P = ParamSpec("P")
T = TypeVar("T")


def updates_modified_date(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator that updates date_modified after method execution."""

    @wraps(func)
    def wrapper(self: "UserPreferences", *args: P.args, **kwargs: P.kwargs) -> T:
        result = func(self, *args, **kwargs)
        self.date_modified = datetime.now()
        return result

    return wrapper  # type: ignore[return-value]


@dataclass(slots=True, kw_only=True)
class UserPreferences:
    """Stores user preferences and configuration.

    This is a singleton entity - only one instance exists per user.

    Attributes:
        id_: Unique identifier (always the same UUID for singleton).
        default_download_path: Default path to save downloads.
        favorite_paths: User's favorite download locations.
        favorite_aggregators: Preferred torrent sources.
        max_concurrent_downloads: Maximum simultaneous downloads.
        auto_start_downloads: Auto-start downloads on add.
        date_created: When preferences were first created.
        date_modified: Last modification time.
    """

    default_download_path: Path
    id_: UUID = USER_PREFERENCES_ID
    favorite_paths: list[Path] = field(default_factory=list)
    favorite_aggregators: list[AggregatorSource] = field(default_factory=list)
    max_concurrent_downloads: int = 3
    auto_start_downloads: bool = True
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate preferences."""
        if not (1 <= self.max_concurrent_downloads <= 10):
            raise ValidationError("max_concurrent_downloads must be between 1 and 10")

    @classmethod
    def create_default(cls) -> "UserPreferences":
        """Create UserPreferences with default values.

        Returns:
            A new UserPreferences instance with sensible defaults.
        """
        return cls(default_download_path=Path.home() / "Downloads")

    @updates_modified_date
    def add_favorite_path(self, path: Path) -> None:
        """Add path to favorites if not already present.

        Args:
            path: The path to add to favorites.
        """
        if path not in self.favorite_paths:
            self.favorite_paths.append(path)

    @updates_modified_date
    def remove_favorite_path(self, path: Path) -> None:
        """Remove path from favorites.

        Args:
            path: The path to remove from favorites.
        """
        if path in self.favorite_paths:
            self.favorite_paths.remove(path)

    @updates_modified_date
    def add_favorite_aggregator(self, source: AggregatorSource) -> None:
        """Add aggregator to favorites if not already present.

        Args:
            source: The aggregator source to add.
        """
        if source not in self.favorite_aggregators:
            self.favorite_aggregators.append(source)

    @updates_modified_date
    def remove_favorite_aggregator(self, source: AggregatorSource) -> None:
        """Remove aggregator from favorites.

        Args:
            source: The aggregator source to remove.
        """
        if source in self.favorite_aggregators:
            self.favorite_aggregators.remove(source)

    @updates_modified_date
    def update_default_path(self, path: Path) -> None:
        """Change default download path.

        Args:
            path: The new default download path.
        """
        self.default_download_path = path

    @updates_modified_date
    def update_max_concurrent_downloads(self, max_count: int) -> None:
        """Update max concurrent downloads with validation.

        Args:
            max_count: The new maximum concurrent downloads.

        Raises:
            ValidationError: If max_count is not between 1 and 10.
        """
        if not (1 <= max_count <= 10):
            raise ValidationError("max_concurrent_downloads must be between 1 and 10")
        self.max_concurrent_downloads = max_count

    @updates_modified_date
    def update_auto_start(self, enabled: bool) -> None:
        """Toggle auto-start downloads.

        Args:
            enabled: Whether to auto-start downloads.
        """
        self.auto_start_downloads = enabled
