"""Tests for AddFavoritePath use case."""

from pathlib import Path
from unittest.mock import Mock

from nodo.application.use_cases.add_favorite_path import AddFavoritePath
from nodo.domain.entities import UserPreferences


def test_add_favorite_path_adds_new_path() -> None:
    """Should add a new path to favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoritePath(preferences_repository=mock_repo)
    input_data = AddFavoritePath.Input(path=Path("/home/user/Movies"))
    result = use_case.execute(input_data)

    assert result.path == "/home/user/Movies"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_path_does_not_duplicate_existing_path() -> None:
    """Should not add path if it already exists in favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[Path("/home/user/Movies")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoritePath(preferences_repository=mock_repo)
    input_data = AddFavoritePath.Input(path=Path("/home/user/Movies"))
    result = use_case.execute(input_data)

    assert result.path == "/home/user/Movies"
    assert result.added is False
    mock_repo.save.assert_called_once()


def test_add_favorite_path_adds_to_existing_list() -> None:
    """Should add path to existing favorites list."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[Path("/home/user/Movies")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoritePath(preferences_repository=mock_repo)
    input_data = AddFavoritePath.Input(path=Path("/home/user/Music"))
    result = use_case.execute(input_data)

    assert result.path == "/home/user/Music"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_path_calls_repository_methods() -> None:
    """Should call repository.get() and repository.save()."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_paths=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoritePath(preferences_repository=mock_repo)
    input_data = AddFavoritePath.Input(path=Path("/home/user/Movies"))
    use_case.execute(input_data)

    mock_repo.get.assert_called_once()
    mock_repo.save.assert_called_once()
