"""Tests for AddFavoriteAggregator use case."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from nodo.application.use_cases.add_favorite_aggregator import AddFavoriteAggregator
from nodo.domain.entities import UserPreferences
from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import AggregatorSource


def test_add_favorite_aggregator_adds_new_aggregator() -> None:
    """Should add a new aggregator to favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteAggregator(preferences_repository=mock_repo)
    input_data = AddFavoriteAggregator.Input(aggregator_name="1337x")
    result = use_case.execute(input_data)

    assert result.aggregator_name == "1337x"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_aggregator_does_not_duplicate_existing() -> None:
    """Should not add aggregator if it already exists in favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[AggregatorSource(name="1337x")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteAggregator(preferences_repository=mock_repo)
    input_data = AddFavoriteAggregator.Input(aggregator_name="1337x")
    result = use_case.execute(input_data)

    assert result.aggregator_name == "1337x"
    assert result.added is False
    mock_repo.save.assert_called_once()


def test_add_favorite_aggregator_adds_to_existing_list() -> None:
    """Should add aggregator to existing favorites list."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[AggregatorSource(name="1337x")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteAggregator(preferences_repository=mock_repo)
    input_data = AddFavoriteAggregator.Input(aggregator_name="ThePirateBay")
    result = use_case.execute(input_data)

    assert result.aggregator_name == "ThePirateBay"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_aggregator_normalizes_name() -> None:
    """Should normalize aggregator name to canonical format."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteAggregator(preferences_repository=mock_repo)
    input_data = AddFavoriteAggregator.Input(aggregator_name="1337X")  # Different case
    result = use_case.execute(input_data)

    # Should normalize to canonical format
    assert result.aggregator_name == "1337x"
    assert result.added is True
    mock_repo.save.assert_called_once()


def test_add_favorite_aggregator_raises_validation_error_for_empty_name() -> None:
    """Should raise ValidationError for empty aggregator name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteAggregator(preferences_repository=mock_repo)
    input_data = AddFavoriteAggregator.Input(aggregator_name="")

    with pytest.raises(ValidationError, match="Aggregator name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_add_favorite_aggregator_raises_validation_error_for_whitespace() -> None:
    """Should raise ValidationError for whitespace-only name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteAggregator(preferences_repository=mock_repo)
    input_data = AddFavoriteAggregator.Input(aggregator_name="   ")

    with pytest.raises(ValidationError, match="Aggregator name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_add_favorite_aggregator_calls_repository_methods() -> None:
    """Should call repository.get() and repository.save()."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = AddFavoriteAggregator(preferences_repository=mock_repo)
    input_data = AddFavoriteAggregator.Input(aggregator_name="1337x")
    use_case.execute(input_data)

    mock_repo.get.assert_called_once()
    mock_repo.save.assert_called_once()
