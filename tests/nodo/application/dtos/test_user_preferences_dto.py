"""Tests for UserPreferencesDTO."""

from datetime import datetime

import pytest

from nodo.application.dtos import UserPreferencesDTO


def test_user_preferences_dto_create_with_all_fields() -> None:
    """Should create UserPreferencesDTO with all fields."""
    date_created = datetime(2025, 1, 1, 12, 0, 0)
    date_modified = datetime(2025, 1, 2, 12, 0, 0)

    dto = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=["/home/user/Movies", "/home/user/Music"],
        favorite_aggregators=["1337x", "ThePirateBay"],
        max_concurrent_downloads=5,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    assert dto.id_ == "00000000-0000-0000-0000-000000000001"
    assert dto.default_download_path == "/home/user/Downloads"
    assert dto.favorite_paths == ["/home/user/Movies", "/home/user/Music"]
    assert dto.favorite_aggregators == ["1337x", "ThePirateBay"]
    assert dto.max_concurrent_downloads == 5
    assert dto.auto_start_downloads is True
    assert dto.date_created == date_created
    assert dto.date_modified == date_modified


def test_user_preferences_dto_create_with_empty_lists() -> None:
    """Should create UserPreferencesDTO with empty favorite lists."""
    date_created = datetime(2025, 1, 1, 12, 0, 0)
    date_modified = datetime(2025, 1, 1, 12, 0, 0)

    dto = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=[],
        favorite_aggregators=[],
        max_concurrent_downloads=3,
        auto_start_downloads=False,
        date_created=date_created,
        date_modified=date_modified,
    )

    assert dto.favorite_paths == []
    assert dto.favorite_aggregators == []
    assert dto.auto_start_downloads is False


def test_user_preferences_dto_is_frozen() -> None:
    """Should be immutable (frozen dataclass)."""
    date_created = datetime(2025, 1, 1, 12, 0, 0)
    date_modified = datetime(2025, 1, 1, 12, 0, 0)

    dto = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=[],
        favorite_aggregators=[],
        max_concurrent_downloads=3,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    with pytest.raises(Exception):  # noqa: B017, PT011
        dto.default_download_path = "/modified"  # type: ignore[misc]


def test_user_preferences_dto_equality() -> None:
    """Should compare DTOs by value."""
    date_created = datetime(2025, 1, 1, 12, 0, 0)
    date_modified = datetime(2025, 1, 1, 12, 0, 0)

    dto1 = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=["/home/user/Movies"],
        favorite_aggregators=["1337x"],
        max_concurrent_downloads=3,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    dto2 = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=["/home/user/Movies"],
        favorite_aggregators=["1337x"],
        max_concurrent_downloads=3,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    assert dto1 == dto2
    # Note: DTOs with list fields are not hashable, so we can't test hash equality


def test_user_preferences_dto_different_values_not_equal() -> None:
    """Should not be equal when values differ."""
    date_created = datetime(2025, 1, 1, 12, 0, 0)
    date_modified = datetime(2025, 1, 1, 12, 0, 0)

    dto1 = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=["/home/user/Movies"],
        favorite_aggregators=["1337x"],
        max_concurrent_downloads=3,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    dto2 = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=["/home/user/Movies"],
        favorite_aggregators=["1337x"],
        max_concurrent_downloads=5,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    assert dto1 != dto2


def test_user_preferences_dto_with_different_list_order_not_equal() -> None:
    """Should not be equal when list order differs."""
    date_created = datetime(2025, 1, 1, 12, 0, 0)
    date_modified = datetime(2025, 1, 1, 12, 0, 0)

    dto1 = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=["/home/user/Movies", "/home/user/Music"],
        favorite_aggregators=["1337x", "ThePirateBay"],
        max_concurrent_downloads=3,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    dto2 = UserPreferencesDTO(
        id_="00000000-0000-0000-0000-000000000001",
        default_download_path="/home/user/Downloads",
        favorite_paths=["/home/user/Music", "/home/user/Movies"],
        favorite_aggregators=["ThePirateBay", "1337x"],
        max_concurrent_downloads=3,
        auto_start_downloads=True,
        date_created=date_created,
        date_modified=date_modified,
    )

    # Lists are compared by value, so order matters
    assert dto1 != dto2
