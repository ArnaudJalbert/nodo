"""Tests for RemoveFavoritePath use case."""

from pathlib import Path
from unittest.mock import Mock

from nodo.application.use_cases.remove_favorite_path import RemoveFavoritePath
from nodo.domain.entities import UserPreferences


def test_remove_favorite_path_removes_existing_path() -> None:
    """Should remove path from favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[Path("/home/user/Movies"), Path("/home/user/Music")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoritePath(preferences_repository=mock_repo)
    input_data = RemoveFavoritePath.Input(path=Path("/home/user/Movies"))
    result = use_case.execute(input_data)

    assert result.path == "/home/user/Movies"
    assert result.removed is True
    mock_repo.save.assert_called_once()


def test_remove_favorite_path_handles_nonexistent_path() -> None:
    """Should handle removal of path that doesn't exist."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[Path("/home/user/Movies")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoritePath(preferences_repository=mock_repo)
    input_data = RemoveFavoritePath.Input(path=Path("/home/user/Music"))
    result = use_case.execute(input_data)

    assert result.path == "/home/user/Music"
    assert result.removed is False
    mock_repo.save.assert_called_once()


def test_remove_favorite_path_from_empty_list() -> None:
    """Should handle removal from empty favorites list."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoritePath(preferences_repository=mock_repo)
    input_data = RemoveFavoritePath.Input(path=Path("/home/user/Movies"))
    result = use_case.execute(input_data)

    assert result.path == "/home/user/Movies"
    assert result.removed is False
    mock_repo.save.assert_called_once()


def test_remove_favorite_path_calls_repository_methods() -> None:
    """Should call repository.get() and repository.save()."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[Path("/home/user/Movies")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoritePath(preferences_repository=mock_repo)
    input_data = RemoveFavoritePath.Input(path=Path("/home/user/Movies"))
    use_case.execute(input_data)

    mock_repo.get.assert_called_once()
    mock_repo.save.assert_called_once()
