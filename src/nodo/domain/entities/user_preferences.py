"""User preferences entity."""

from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar
from uuid import UUID

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import IndexerSource

# Well-known singleton UUID for UserPreferences
USER_PREFERENCES_ID = UUID("00000000-0000-0000-0000-000000000001")

P = ParamSpec("P")
T = TypeVar("T")


def updates_modified_date(
    func: Callable[P, T] | None = None, *, only_when_changed: bool = False
) -> Callable[P, T]:
    """Decorator that updates date_modified after method execution.

    Args:
        func: The wrapped method.
        only_when_changed: Whether to update date_modified only when the wrapped method
            returns a truthy value indicating a mutation occurred.
    """

    def decorator(inner_func: Callable[P, T]) -> Callable[P, T]:
        @wraps(inner_func)
        def wrapper(self: "UserPreferences", *args: P.args, **kwargs: P.kwargs) -> T:
            result = inner_func(self, *args, **kwargs)
            should_update = True
            if only_when_changed:
                should_update = bool(result)
            if should_update:
                self.date_modified = datetime.now()
            return result

        return wrapper  # type: ignore[return-value]

    if func is not None:
        return decorator(func)
    return decorator


@dataclass(slots=True, kw_only=True)
class UserPreferences:
    """Stores user preferences and configuration.

    This is a singleton entity - only one instance exists per user.

    Attributes:
        id_: Unique identifier (always the same UUID for singleton).
        default_download_path: Default path to save downloads.
        favorite_paths: User's favorite download locations.
        favorite_indexers: Preferred torrent indexer sources.
        max_concurrent_downloads: Maximum simultaneous downloads.
        auto_start_downloads: Auto-start downloads on add.
        date_created: When preferences were first created.
        date_modified: Last modification time.
    """

    default_download_path: Path
    id_: UUID = USER_PREFERENCES_ID
    favorite_paths: list[Path] = field(default_factory=list)
    favorite_indexers: list[IndexerSource] = field(default_factory=list)
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

    @updates_modified_date(only_when_changed=True)
    def add_favorite_path(self, path: Path) -> bool:
        """Add path to favorites if not already present.

        Args:
            path: The path to add to favorites.

        Returns:
            True if the path was added, False otherwise.
        """
        if path not in self.favorite_paths:
            self.favorite_paths.append(path)
            return True
        return False

    @updates_modified_date(only_when_changed=True)
    def remove_favorite_path(self, path: Path) -> bool:
        """Remove path from favorites.

        Args:
            path: The path to remove from favorites.

        Returns:
            True if the path was removed, False otherwise.
        """
        if path in self.favorite_paths:
            self.favorite_paths.remove(path)
            return True
        return False

    @updates_modified_date(only_when_changed=True)
    def add_favorite_indexer(self, source: IndexerSource) -> bool:
        """Add indexer to favorites if not already present.

        Args:
            source: The indexer source to add.

        Returns:
            True if the indexer was added, False otherwise.
        """
        if source not in self.favorite_indexers:
            self.favorite_indexers.append(source)
            return True
        return False

    @updates_modified_date(only_when_changed=True)
    def remove_favorite_indexer(self, source: IndexerSource) -> bool:
        """Remove indexer from favorites.

        Args:
            source: The indexer source to remove.

        Returns:
            True if the indexer was removed, False otherwise.
        """
        if source in self.favorite_indexers:
            self.favorite_indexers.remove(source)
            return True
        return False

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
