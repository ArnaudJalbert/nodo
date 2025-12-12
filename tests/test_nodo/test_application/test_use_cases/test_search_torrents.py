"""Tests for SearchTorrents use case."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from nodo.application.interfaces import (
    IndexerManager,
    IUserPreferencesRepository,
)
from nodo.application.use_cases.search_torrents import SearchTorrents
from nodo.domain.entities import TorrentSearchResult, UserPreferences
from nodo.domain.exceptions import (
    IndexerError,
    IndexerTimeoutError,
    ValidationError,
)
from nodo.domain.value_objects import (
    FileSize,
    IndexerSource,
    MagnetLink,
)


def test_search_torrents_success() -> None:
    """Should successfully search and return results."""
    query = "ubuntu"

    result1 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Ubuntu 24.04",
        size=FileSize.from_bytes(4 * 1024 * 1024 * 1024),
        seeders=100,
        leechers=10,
        source=IndexerSource.from_string("Prowlarr"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.search.return_value = [result1]
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    output = use_case.execute(SearchTorrents.Input(query=query))

    assert len(output.results) == 1
    assert output.results[0].title == "Ubuntu 24.04"
    assert output.results[0].seeders == 100
    mock_indexer_manager.search.assert_called_once()


def test_search_torrents_sorts_by_seeders() -> None:
    """Should sort results by seeders descending."""
    result1 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Low seeders",
        size=FileSize.from_bytes(1024),
        seeders=10,
        leechers=5,
        source=IndexerSource.from_string("Prowlarr"),
        date_found=datetime.now(),
    )
    result2 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="High seeders",
        size=FileSize.from_bytes(1024),
        seeders=100,
        leechers=10,
        source=IndexerSource.from_string("Prowlarr"),
        date_found=datetime.now(),
    )

    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.search.return_value = [result1, result2]
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    output = use_case.execute(SearchTorrents.Input(query="test"))

    assert output.results[0].seeders == 100
    assert output.results[1].seeders == 10


def test_search_torrents_uses_favorite_indexers() -> None:
    """Should use favorite indexers from preferences."""
    result = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Test",
        size=FileSize.from_bytes(1024),
        seeders=50,
        leechers=5,
        source=IndexerSource.from_string("Prowlarr"),
        date_found=datetime.now(),
    )

    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.search.return_value = [result]
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    prefs = UserPreferences.create_default()
    prefs.add_favorite_indexer(IndexerSource.from_string("Prowlarr"))

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = prefs

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    output = use_case.execute(SearchTorrents.Input(query="test"))

    assert len(output.results) == 1


def test_search_torrents_with_specific_indexers() -> None:
    """Should search specific indexers when provided."""
    result = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Test",
        size=FileSize.from_bytes(1024),
        seeders=50,
        leechers=5,
        source=IndexerSource.from_string("Prowlarr"),
        date_found=datetime.now(),
    )

    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.search.return_value = [result]
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    output = use_case.execute(
        SearchTorrents.Input(query="test", indexer_names=["Prowlarr"])
    )

    assert len(output.results) == 1
    call_args = mock_indexer_manager.search.call_args
    assert call_args[1]["indexer_names"] == ["Prowlarr"]


def test_search_torrents_raises_error_for_empty_query() -> None:
    """Should raise ValidationError for empty query."""
    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    with pytest.raises(ValidationError, match="cannot be empty"):
        use_case.execute(SearchTorrents.Input(query=""))


def test_search_torrents_raises_error_for_invalid_max_results() -> None:
    """Should raise ValidationError for invalid max_results."""
    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    with pytest.raises(ValidationError, match="must be at least 1"):
        use_case.execute(SearchTorrents.Input(query="test", max_results=0))


def test_search_torrents_raises_error_for_invalid_indexer_name() -> None:
    """Should raise ValidationError for invalid indexer name."""
    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    with pytest.raises(ValidationError, match="Invalid indexer names"):
        use_case.execute(
            SearchTorrents.Input(query="test", indexer_names=["InvalidSource"])
        )


def test_search_torrents_raises_indexer_error_on_failure() -> None:
    """Should propagate IndexerError from indexer manager."""
    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.search.side_effect = IndexerError("Search failed")
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    with pytest.raises(IndexerError):
        use_case.execute(SearchTorrents.Input(query="test"))


def test_search_torrents_raises_indexer_timeout_error() -> None:
    """Should propagate IndexerTimeoutError from indexer manager."""
    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.search.side_effect = IndexerTimeoutError("Timeout")
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    with pytest.raises(IndexerTimeoutError):
        use_case.execute(SearchTorrents.Input(query="test"))


def test_search_torrents_raises_error_for_empty_indexer_names_list() -> None:
    """Should raise ValidationError when indexer_names list is empty."""
    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.get_available_indexers.return_value = ["Prowlarr"]

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    with pytest.raises(ValidationError, match="at least one indexer name"):
        use_case.execute(SearchTorrents.Input(query="test", indexer_names=[]))


def test_search_torrents_raises_error_when_no_indexers_available() -> None:
    """Should raise IndexerError when no indexers are available for search."""
    mock_indexer_manager = Mock(spec=IndexerManager)
    mock_indexer_manager.get_available_indexers.return_value = []

    mock_prefs_repo = Mock(spec=IUserPreferencesRepository)
    prefs = UserPreferences.create_default()
    # No favorite indexers added
    mock_prefs_repo.get.return_value = prefs

    use_case = SearchTorrents(
        indexer_manager=mock_indexer_manager,
        preferences_repository=mock_prefs_repo,
    )

    with pytest.raises(IndexerError, match="No indexers available"):
        use_case.execute(SearchTorrents.Input(query="test"))
