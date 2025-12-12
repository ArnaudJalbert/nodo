"""Tests for RemoveFavoriteIndexer use case."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from nodo.application.interfaces import IUserPreferencesRepository
from nodo.application.use_cases.remove_favorite_indexer import (
    RemoveFavoriteIndexer,
)
from nodo.domain.entities import UserPreferences
from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import IndexerSource


def test_remove_favorite_indexer_removes_existing() -> None:
    """Should remove aggregator from favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[
            IndexerSource(name="Prowlarr"),
            IndexerSource(name="Prowlarr"),
        ],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteIndexer(preferences_repository=mock_repo)
    input_data = RemoveFavoriteIndexer.Input(indexer_name="Prowlarr")
    result = use_case.execute(input_data)

    assert result.indexer_name == "Prowlarr"
    assert result.removed is True
    mock_repo.save.assert_called_once()


def test_remove_favorite_indexer_handles_nonexistent() -> None:
    """Should handle removal of indexer that doesn't exist."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[IndexerSource(name="CustomIndexer")],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteIndexer(preferences_repository=mock_repo)
    input_data = RemoveFavoriteIndexer.Input(indexer_name="Prowlarr")
    result = use_case.execute(input_data)

    assert result.indexer_name == "Prowlarr"
    assert result.removed is False
    mock_repo.save.assert_called_once()


def test_remove_favorite_indexer_from_empty_list() -> None:
    """Should handle removal from empty favorites list."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteIndexer(preferences_repository=mock_repo)
    input_data = RemoveFavoriteIndexer.Input(indexer_name="Prowlarr")
    result = use_case.execute(input_data)

    assert result.indexer_name == "Prowlarr"
    assert result.removed is False
    mock_repo.save.assert_called_once()


def test_remove_favorite_indexer_normalizes_name() -> None:
    """Should normalize aggregator name for case-insensitive removal."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[IndexerSource(name="Prowlarr")],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteIndexer(preferences_repository=mock_repo)
    input_data = RemoveFavoriteIndexer.Input(indexer_name="Prowlarr")  # Different case
    result = use_case.execute(input_data)

    assert result.indexer_name == "Prowlarr"
    assert result.removed is True
    mock_repo.save.assert_called_once()


def test_remove_favorite_indexer_raises_validation_error_for_empty_name() -> None:
    """Should raise ValidationError for empty aggregator name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteIndexer(preferences_repository=mock_repo)
    input_data = RemoveFavoriteIndexer.Input(indexer_name="")

    with pytest.raises(ValidationError, match="Indexer name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_remove_favorite_indexer_raises_validation_error_for_whitespace() -> None:
    """Should raise ValidationError for whitespace-only name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteIndexer(preferences_repository=mock_repo)
    input_data = RemoveFavoriteIndexer.Input(indexer_name="   ")

    with pytest.raises(ValidationError, match="Indexer name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_remove_favorite_indexer_calls_repository_methods() -> None:
    """Should call repository.get() and repository.save()."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[IndexerSource(name="Prowlarr")],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteIndexer(preferences_repository=mock_repo)
    input_data = RemoveFavoriteIndexer.Input(indexer_name="Prowlarr")
    use_case.execute(input_data)

    mock_repo.get.assert_called_once()
    mock_repo.save.assert_called_once()
