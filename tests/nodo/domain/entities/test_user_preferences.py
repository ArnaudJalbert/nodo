"""Tests for UserPreferences entity."""

from datetime import datetime
from pathlib import Path
from time import sleep

import pytest

from nodo.domain.entities import USER_PREFERENCES_ID, UserPreferences
from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import AggregatorSource

# --- Creation ---


def test_user_preferences_create_with_default_path() -> None:
    """Should create UserPreferences with required default_download_path."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))

    assert prefs.default_download_path == Path("/downloads")
    assert prefs.id_ == USER_PREFERENCES_ID
    assert prefs.favorite_paths == []
    assert prefs.favorite_aggregators == []
    assert prefs.max_concurrent_downloads == 3
    assert prefs.auto_start_downloads is True
    assert isinstance(prefs.date_created, datetime)
    assert isinstance(prefs.date_modified, datetime)


def test_user_preferences_create_default_factory() -> None:
    """Should create UserPreferences with sensible defaults via factory."""
    prefs = UserPreferences.create_default()

    assert prefs.default_download_path == Path.home() / "Downloads"
    assert prefs.id_ == USER_PREFERENCES_ID


def test_user_preferences_create_with_all_fields() -> None:
    """Should create UserPreferences with all fields specified."""
    date_created = datetime(2025, 1, 1)
    date_modified = datetime(2025, 1, 15)
    favorite_paths = [Path("/movies"), Path("/music")]
    favorite_aggregators = [AggregatorSource(name="1337x")]

    prefs = UserPreferences(
        default_download_path=Path("/downloads"),
        favorite_paths=favorite_paths,
        favorite_aggregators=favorite_aggregators,
        max_concurrent_downloads=5,
        auto_start_downloads=False,
        date_created=date_created,
        date_modified=date_modified,
    )

    assert prefs.favorite_paths == favorite_paths
    assert prefs.favorite_aggregators == favorite_aggregators
    assert prefs.max_concurrent_downloads == 5
    assert prefs.auto_start_downloads is False
    assert prefs.date_created == date_created
    assert prefs.date_modified == date_modified


def test_user_preferences_reject_invalid_max_concurrent_downloads_zero() -> None:
    """Should reject max_concurrent_downloads of 0."""
    with pytest.raises(ValidationError, match="must be between 1 and 10"):
        UserPreferences(
            default_download_path=Path("/downloads"), max_concurrent_downloads=0
        )


def test_user_preferences_reject_invalid_max_concurrent_downloads_negative() -> None:
    """Should reject negative max_concurrent_downloads."""
    with pytest.raises(ValidationError, match="must be between 1 and 10"):
        UserPreferences(
            default_download_path=Path("/downloads"), max_concurrent_downloads=-1
        )


def test_user_preferences_reject_invalid_max_concurrent_downloads_too_high() -> None:
    """Should reject max_concurrent_downloads above 10."""
    with pytest.raises(ValidationError, match="must be between 1 and 10"):
        UserPreferences(
            default_download_path=Path("/downloads"), max_concurrent_downloads=11
        )


# --- Favorite Paths ---


def test_user_preferences_add_favorite_path() -> None:
    """Should add path to favorites."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.add_favorite_path(Path("/movies"))

    assert Path("/movies") in prefs.favorite_paths


def test_user_preferences_add_favorite_path_updates_date_modified() -> None:
    """Adding favorite path should update date_modified."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    original_modified = prefs.date_modified
    sleep(0.01)

    prefs.add_favorite_path(Path("/movies"))

    assert prefs.date_modified > original_modified


def test_user_preferences_add_duplicate_favorite_path_no_effect() -> None:
    """Adding duplicate path should not add it again."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.add_favorite_path(Path("/movies"))
    prefs.add_favorite_path(Path("/movies"))

    assert prefs.favorite_paths.count(Path("/movies")) == 1


def test_user_preferences_remove_favorite_path() -> None:
    """Should remove path from favorites."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.add_favorite_path(Path("/movies"))
    prefs.remove_favorite_path(Path("/movies"))

    assert Path("/movies") not in prefs.favorite_paths


def test_user_preferences_remove_favorite_path_updates_date_modified() -> None:
    """Removing favorite path should update date_modified."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.add_favorite_path(Path("/movies"))
    original_modified = prefs.date_modified
    sleep(0.01)

    prefs.remove_favorite_path(Path("/movies"))

    assert prefs.date_modified > original_modified


def test_user_preferences_remove_nonexistent_path_no_error() -> None:
    """Removing nonexistent path should not raise error."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.remove_favorite_path(Path("/nonexistent"))

    assert Path("/nonexistent") not in prefs.favorite_paths


# --- Favorite Aggregators ---


def test_user_preferences_add_favorite_aggregator() -> None:
    """Should add aggregator to favorites."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    source = AggregatorSource(name="1337x")
    prefs.add_favorite_aggregator(source)

    assert source in prefs.favorite_aggregators


def test_user_preferences_add_favorite_aggregator_updates_date_modified() -> None:
    """Adding favorite aggregator should update date_modified."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    original_modified = prefs.date_modified
    sleep(0.01)

    prefs.add_favorite_aggregator(AggregatorSource(name="1337x"))

    assert prefs.date_modified > original_modified


def test_user_preferences_add_duplicate_favorite_aggregator_no_effect() -> None:
    """Adding duplicate aggregator should not add it again."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    source = AggregatorSource(name="1337x")
    prefs.add_favorite_aggregator(source)
    prefs.add_favorite_aggregator(source)

    assert len([a for a in prefs.favorite_aggregators if a == source]) == 1


def test_user_preferences_remove_favorite_aggregator() -> None:
    """Should remove aggregator from favorites."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    source = AggregatorSource(name="1337x")
    prefs.add_favorite_aggregator(source)
    prefs.remove_favorite_aggregator(source)

    assert source not in prefs.favorite_aggregators


def test_user_preferences_remove_favorite_aggregator_updates_date_modified() -> None:
    """Removing favorite aggregator should update date_modified."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    source = AggregatorSource(name="1337x")
    prefs.add_favorite_aggregator(source)
    original_modified = prefs.date_modified
    sleep(0.01)

    prefs.remove_favorite_aggregator(source)

    assert prefs.date_modified > original_modified


# --- Update Methods ---


def test_user_preferences_update_default_path() -> None:
    """Should update default download path."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.update_default_path(Path("/new/downloads"))

    assert prefs.default_download_path == Path("/new/downloads")


def test_user_preferences_update_default_path_updates_date_modified() -> None:
    """Updating default path should update date_modified."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    original_modified = prefs.date_modified
    sleep(0.01)

    prefs.update_default_path(Path("/new/downloads"))

    assert prefs.date_modified > original_modified


def test_user_preferences_update_max_concurrent_downloads() -> None:
    """Should update max concurrent downloads."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.update_max_concurrent_downloads(5)

    assert prefs.max_concurrent_downloads == 5


def test_user_preferences_update_max_concurrent_downloads_updates_date_modified() -> (
    None
):
    """Updating max concurrent downloads should update date_modified."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    original_modified = prefs.date_modified
    sleep(0.01)

    prefs.update_max_concurrent_downloads(5)

    assert prefs.date_modified > original_modified


def test_user_preferences_update_max_concurrent_downloads_validates() -> None:
    """Should validate max concurrent downloads on update."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))

    with pytest.raises(ValidationError, match="must be between 1 and 10"):
        prefs.update_max_concurrent_downloads(0)


def test_user_preferences_update_auto_start() -> None:
    """Should update auto start setting."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    prefs.update_auto_start(False)

    assert prefs.auto_start_downloads is False


def test_user_preferences_update_auto_start_updates_date_modified() -> None:
    """Updating auto start should update date_modified."""
    prefs = UserPreferences(default_download_path=Path("/downloads"))
    original_modified = prefs.date_modified
    sleep(0.01)

    prefs.update_auto_start(False)

    assert prefs.date_modified > original_modified
