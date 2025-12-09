"""Tests for UpdateUserPreferences use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from nodo.application.use_cases.update_user_preferences import UpdateUserPreferences
from nodo.domain.entities import UserPreferences
from nodo.domain.exceptions import ValidationError


def test_update_user_preferences_updates_default_path() -> None:
    """Should update default download path."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        date_created=datetime(2025, 1, 1, 12, 0, 0),
        date_modified=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = UpdateUserPreferences(preferences_repository=mock_repo)
    input_data = UpdateUserPreferences.Input(
        default_download_path=Path("/home/user/Movies")
    )
    result = use_case.execute(input_data)

    assert result.default_download_path == "/home/user/Movies"
    assert result.max_concurrent_downloads is None
    assert result.auto_start_downloads is None
    mock_repo.save.assert_called_once()


def test_update_user_preferences_updates_max_concurrent() -> None:
    """Should update max concurrent downloads."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        max_concurrent_downloads=3,
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = UpdateUserPreferences(preferences_repository=mock_repo)
    input_data = UpdateUserPreferences.Input(max_concurrent_downloads=7)
    result = use_case.execute(input_data)

    assert result.max_concurrent_downloads == 7
    assert result.default_download_path is None
    assert result.auto_start_downloads is None
    mock_repo.save.assert_called_once()


def test_update_user_preferences_updates_auto_start() -> None:
    """Should update auto-start downloads setting."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        auto_start_downloads=True,
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = UpdateUserPreferences(preferences_repository=mock_repo)
    input_data = UpdateUserPreferences.Input(auto_start_downloads=False)
    result = use_case.execute(input_data)

    assert result.auto_start_downloads is False
    assert result.default_download_path is None
    assert result.max_concurrent_downloads is None
    mock_repo.save.assert_called_once()


def test_update_user_preferences_updates_multiple_fields() -> None:
    """Should update multiple fields at once."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        max_concurrent_downloads=3,
        auto_start_downloads=True,
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = UpdateUserPreferences(preferences_repository=mock_repo)
    input_data = UpdateUserPreferences.Input(
        default_download_path=Path("/home/user/Movies"),
        max_concurrent_downloads=5,
        auto_start_downloads=False,
    )
    result = use_case.execute(input_data)

    assert result.default_download_path == "/home/user/Movies"
    assert result.max_concurrent_downloads == 5
    assert result.auto_start_downloads is False
    mock_repo.save.assert_called_once()


def test_update_user_preferences_with_no_changes() -> None:
    """Should return all None when no parameters provided."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        max_concurrent_downloads=3,
        auto_start_downloads=True,
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = UpdateUserPreferences(preferences_repository=mock_repo)
    input_data = UpdateUserPreferences.Input()
    result = use_case.execute(input_data)

    assert result.default_download_path is None
    assert result.max_concurrent_downloads is None
    assert result.auto_start_downloads is None
    mock_repo.save.assert_called_once()


def test_update_user_preferences_raises_validation_error_for_invalid_max() -> None:
    """Should raise ValidationError for invalid max_concurrent_downloads."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        max_concurrent_downloads=3,
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = UpdateUserPreferences(preferences_repository=mock_repo)
    input_data = UpdateUserPreferences.Input(max_concurrent_downloads=15)

    with pytest.raises(
        ValidationError, match="max_concurrent_downloads must be between 1 and 10"
    ):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_update_user_preferences_raises_validation_error_for_zero_max() -> None:
    """Should raise ValidationError for zero max_concurrent_downloads."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        max_concurrent_downloads=3,
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = UpdateUserPreferences(preferences_repository=mock_repo)
    input_data = UpdateUserPreferences.Input(max_concurrent_downloads=0)

    with pytest.raises(
        ValidationError, match="max_concurrent_downloads must be between 1 and 10"
    ):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()
