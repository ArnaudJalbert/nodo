"""Tests for RemoveFavoriteAggregator use case."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from nodo.application.use_cases.remove_favorite_aggregator import (
    RemoveFavoriteAggregator,
)
from nodo.domain.entities import UserPreferences
from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import AggregatorSource


def test_remove_favorite_aggregator_removes_existing() -> None:
    """Should remove aggregator from favorites."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[
            AggregatorSource(name="1337x"),
            AggregatorSource(name="ThePirateBay"),
        ],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteAggregator(preferences_repository=mock_repo)
    input_data = RemoveFavoriteAggregator.Input(aggregator_name="1337x")
    result = use_case.execute(input_data)

    assert result.aggregator_name == "1337x"
    assert result.removed is True
    mock_repo.save.assert_called_once()


def test_remove_favorite_aggregator_handles_nonexistent() -> None:
    """Should handle removal of aggregator that doesn't exist."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[AggregatorSource(name="1337x")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteAggregator(preferences_repository=mock_repo)
    input_data = RemoveFavoriteAggregator.Input(aggregator_name="ThePirateBay")
    result = use_case.execute(input_data)

    assert result.aggregator_name == "ThePirateBay"
    assert result.removed is False
    mock_repo.save.assert_called_once()


def test_remove_favorite_aggregator_from_empty_list() -> None:
    """Should handle removal from empty favorites list."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteAggregator(preferences_repository=mock_repo)
    input_data = RemoveFavoriteAggregator.Input(aggregator_name="1337x")
    result = use_case.execute(input_data)

    assert result.aggregator_name == "1337x"
    assert result.removed is False
    mock_repo.save.assert_called_once()


def test_remove_favorite_aggregator_normalizes_name() -> None:
    """Should normalize aggregator name for case-insensitive removal."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[AggregatorSource(name="1337x")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteAggregator(preferences_repository=mock_repo)
    input_data = RemoveFavoriteAggregator.Input(
        aggregator_name="1337X"
    )  # Different case
    result = use_case.execute(input_data)

    assert result.aggregator_name == "1337x"
    assert result.removed is True
    mock_repo.save.assert_called_once()


def test_remove_favorite_aggregator_raises_validation_error_for_empty_name() -> None:
    """Should raise ValidationError for empty aggregator name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteAggregator(preferences_repository=mock_repo)
    input_data = RemoveFavoriteAggregator.Input(aggregator_name="")

    with pytest.raises(ValidationError, match="Aggregator name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_remove_favorite_aggregator_raises_validation_error_for_whitespace() -> None:
    """Should raise ValidationError for whitespace-only name."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteAggregator(preferences_repository=mock_repo)
    input_data = RemoveFavoriteAggregator.Input(aggregator_name="   ")

    with pytest.raises(ValidationError, match="Aggregator name cannot be empty"):
        use_case.execute(input_data)

    mock_repo.save.assert_not_called()


def test_remove_favorite_aggregator_calls_repository_methods() -> None:
    """Should call repository.get() and repository.save()."""
    preferences = UserPreferences(
        default_download_path=Path("/home/user/Downloads"),
        favorite_aggregators=[AggregatorSource(name="1337x")],
    )

    mock_repo = Mock()
    mock_repo.get.return_value = preferences

    use_case = RemoveFavoriteAggregator(preferences_repository=mock_repo)
    input_data = RemoveFavoriteAggregator.Input(aggregator_name="1337x")
    use_case.execute(input_data)

    mock_repo.get.assert_called_once()
    mock_repo.save.assert_called_once()
