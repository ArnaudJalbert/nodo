"""Tests for GetUserPreferences use case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

from nodo.application.interfaces import IUserPreferencesRepository
from nodo.application.use_cases.get_user_preferences import GetUserPreferences
from nodo.domain.entities import UserPreferences
from nodo.domain.value_objects import IndexerSource


def test_get_user_preferences_returns_output() -> None:
    """Should return Output from repository."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[Path("/home/user/Movies")],
        favorite_indexers=[IndexerSource(name="Prowlarr")],
        max_concurrent_downloads=5,
        auto_start_downloads=True,
        date_created=datetime(2025, 1, 1, 12, 0, 0),
        date_modified=datetime(2025, 1, 2, 12, 0, 0),
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = GetUserPreferences(preferences_repository=mock_repo)
    result = use_case.execute()

    assert isinstance(result, GetUserPreferences.Output)
    assert result.default_download_path == "/home/user/Downloads"
    assert result.favorite_paths == ("/home/user/Movies",)
    assert result.favorite_indexers == ("Prowlarr",)
    assert result.max_concurrent_downloads == 5
    assert result.auto_start_downloads is True
    mock_repo.get.assert_called_once()


def test_get_user_preferences_with_default_preferences() -> None:
    """Should return Output for default preferences."""
    preferences = UserPreferences.create_default()

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = GetUserPreferences(preferences_repository=mock_repo)
    result = use_case.execute()

    assert isinstance(result, GetUserPreferences.Output)
    assert result.favorite_paths == ()
    assert result.favorite_indexers == ()
    assert result.max_concurrent_downloads == 3
    assert result.auto_start_downloads is True


def test_get_user_preferences_calls_repository() -> None:
    """Should call repository.get() method."""
    preferences = UserPreferences.create_default()

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = GetUserPreferences(preferences_repository=mock_repo)
    use_case.execute()

    mock_repo.get.assert_called_once()
