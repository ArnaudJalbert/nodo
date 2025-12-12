"""Tests for AddFavoriteIndexer use case."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from nodo.application.interfaces import IUserPreferencesRepository
from nodo.application.use_cases.add_favorite_indexer import AddFavoriteIndexer
from nodo.domain.entities import UserPreferences
from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import IndexerSource


def test_add_favorite_indexer_adds_new_aggregator() -> None:
    """Should add a new aggregator to favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="Prowlarr")
    result = use_case.execute(input_data)

    assert result.indexer_name == "Prowlarr"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_indexer_does_not_duplicate_existing() -> None:
    """Should not add aggregator if it already exists in favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[IndexerSource(name="Prowlarr")],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="Prowlarr")
    result = use_case.execute(input_data)

    assert result.indexer_name == "Prowlarr"
    assert result.added is False
    mock_repo.save.assert_called_once()


def test_add_favorite_indexer_adds_to_existing_list() -> None:
    """Should add indexer to existing favorites list."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[IndexerSource(name="CustomIndexer")],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="Prowlarr")
    result = use_case.execute(input_data)

    assert result.indexer_name == "Prowlarr"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_indexer_normalizes_name() -> None:
    """Should normalize indexer name to canonical format."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="prowlarr")  # Different case
    result = use_case.execute(input_data)

    # Should normalize to canonical format
    assert result.indexer_name == "Prowlarr"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_indexer_raises_validation_error_for_empty_name() -> None:
    """Should raise ValidationError for empty aggregator name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="")

    with pytest.raises(ValidationError, match="Indexer name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_add_favorite_indexer_raises_validation_error_for_whitespace() -> None:
    """Should raise ValidationError for whitespace-only name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="   ")

    with pytest.raises(ValidationError, match="Indexer name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_add_favorite_indexer_calls_repository_methods() -> None:
    """Should call repository.get() and repository.save()."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="Prowlarr")
    use_case.execute(input_data)

    mock_repo.get.assert_called_once()
    mock_repo.save.assert_called_once()


def test_add_favorite_indexer_raises_error_for_unsupported_aggregator() -> None:
    """Should raise ValidationError for unsupported aggregator name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_indexers=[],
    )

    mock_repo = Mock(spec=IUserPreferencesRepository)
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteIndexer(preferences_repository=mock_repo)
    input_data = AddFavoriteIndexer.Input(indexer_name="InvalidAggregator")

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "unsupported indexer" in str(exc_info.value).lower()
    assert "InvalidAggregator" in str(exc_info.value)
    mock_repo.save.assert_not_called()
