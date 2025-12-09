"""Tests for SearchTorrents use case."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from nodo.application.interfaces import IAggregatorServiceRegistry
from nodo.application.use_cases.search_torrents import SearchTorrents
from nodo.domain.entities import TorrentSearchResult, UserPreferences
from nodo.domain.exceptions import (
    AggregatorError,
    AggregatorTimeoutError,
    ValidationError,
)
from nodo.domain.value_objects import (
    AggregatorSource,
    FileSize,
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
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.return_value = [result1]

    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_service.return_value = mock_service1
    mock_registry.get_all_names.return_value = ["1337x"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query=query, max_results=10)

    result = use_case.execute(input_data)

    assert len(result.results) == 1
    assert result.results[0].title == "Ubuntu 24.04"
    assert result.results[0].seeders == 100
    assert len(result.failed_searches) == 0
    mock_service1.search.assert_called_once_with(query, max_results=10)


def test_search_torrents_multiple_aggregators() -> None:
    """Should search multiple aggregators and combine results."""
    query = "test"

    result1 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Result 1",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    result2 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Result 2",
        size=FileSize.from_bytes(2048 * 1024),
        seeders=75,
        leechers=8,
        source=AggregatorSource.from_string("ThePirateBay"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.return_value = [result1]

    mock_service2 = Mock()
    mock_service2.source = AggregatorSource.from_string("ThePirateBay")
    mock_service2.search.return_value = [result2]

    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service1
        if name == "ThePirateBay":
            return mock_service2
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query=query, aggregator_names=["1337x", "ThePirateBay"]
    )

    result = use_case.execute(input_data)

    assert len(result.results) == 2
    # Results should be sorted by seeders descending
    assert result.results[0].seeders == 75
    assert result.results[1].seeders == 50
    assert len(result.failed_searches) == 0


def test_search_torrents_deduplicates_by_magnet_link() -> None:
    """Should deduplicate results by magnet link."""
    query = "test"
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)

    result1 = TorrentSearchResult(
        magnet_link=magnet_link,
        title="Result from 1337x",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    result2 = TorrentSearchResult(
        magnet_link=magnet_link,  # Same magnet link
        title="Result from TPB",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=75,
        leechers=8,
        source=AggregatorSource.from_string("ThePirateBay"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.return_value = [result1]

    mock_service2 = Mock()
    mock_service2.source = AggregatorSource.from_string("ThePirateBay")
    mock_service2.search.return_value = [result2]

    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service1
        if name == "ThePirateBay":
            return mock_service2
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query=query, aggregator_names=["1337x", "ThePirateBay"]
    )

    result = use_case.execute(input_data)

    # Should only have one result (deduplicated)
    assert len(result.results) == 1
    # Should keep first occurrence (from 1337x)
    assert result.results[0].title == "Result from 1337x"


def test_search_torrents_uses_favorite_aggregators() -> None:
    """Should use favorite aggregators from preferences when none provided."""
    query = "test"

    result = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Result",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service = Mock()
    mock_service.source = AggregatorSource.from_string("1337x")
    mock_service.search.return_value = [result]

    mock_service2 = Mock()
    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service
        if name == "ThePirateBay":
            return mock_service2
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]

    preferences = UserPreferences.create_default()
    preferences.favorite_aggregators = [AggregatorSource.from_string("1337x")]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = preferences

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query=query)

    use_case.execute(input_data)

    # Should only search favorite aggregator
    mock_service.search.assert_called_once()
    # Should not search ThePirateBay
    mock_service2.search.assert_not_called()


def test_search_torrents_uses_all_aggregators_when_no_favorites() -> None:
    """Should use all aggregators when no favorites set."""
    query = "test"

    result1 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Result 1",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    result2 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="Result 2",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=75,
        leechers=8,
        source=AggregatorSource.from_string("ThePirateBay"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.return_value = [result1]

    mock_service2 = Mock()
    mock_service2.source = AggregatorSource.from_string("ThePirateBay")
    mock_service2.search.return_value = [result2]

    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service1
        if name == "ThePirateBay":
            return mock_service2
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query=query)

    result = use_case.execute(input_data)

    # Should search all aggregators
    assert len(result.results) == 2
    mock_service1.search.assert_called_once()
    mock_service2.search.assert_called_once()


def test_search_torrents_handles_aggregator_failure() -> None:
    """Should handle aggregator failures gracefully and track them."""
    query = "test"

    result = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Result",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.return_value = [result]

    mock_service2 = Mock()
    mock_service2.source = AggregatorSource.from_string("ThePirateBay")
    mock_service2.search.side_effect = AggregatorError("Service failed")

    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service1
        if name == "ThePirateBay":
            return mock_service2
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query=query, aggregator_names=["1337x", "ThePirateBay"]
    )

    result = use_case.execute(input_data)

    # Should still return results from successful aggregator
    assert len(result.results) == 1
    assert result.results[0].title == "Result"

    # Should track failed search with specific message
    assert len(result.failed_searches) == 1
    assert result.failed_searches[0].aggregator_name == "ThePirateBay"
    assert result.failed_searches[0].error_message.startswith("Search failed:")
    assert "Service failed" in result.failed_searches[0].error_message


def test_search_torrents_raises_error_when_all_fail() -> None:
    """Should raise AggregatorError when all aggregators fail."""
    query = "test"

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.side_effect = AggregatorError("Service 1 failed")

    mock_service2 = Mock()
    mock_service2.source = AggregatorSource.from_string("ThePirateBay")
    mock_service2.search.side_effect = AggregatorError("Service 2 failed")

    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service1
        if name == "ThePirateBay":
            return mock_service2
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query=query, aggregator_names=["1337x", "ThePirateBay"]
    )

    with pytest.raises(AggregatorError) as exc_info:
        use_case.execute(input_data)

    assert "All aggregators failed" in str(exc_info.value)


def test_search_torrents_tracks_multiple_failed_searches() -> None:
    """Should track multiple failed searches."""
    query = "test"

    result = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Result",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.return_value = [result]

    mock_service2 = Mock()
    mock_service2.source = AggregatorSource.from_string("ThePirateBay")
    mock_service2.search.side_effect = AggregatorError("TPB failed")

    mock_service3 = Mock()
    mock_service3.source = AggregatorSource.from_string("RARBG")
    mock_service3.search.side_effect = AggregatorTimeoutError("RARBG timeout")

    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service1
        if name == "ThePirateBay":
            return mock_service2
        if name == "RARBG":
            return mock_service3
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay", "RARBG"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query=query, aggregator_names=["1337x", "ThePirateBay", "RARBG"]
    )

    result = use_case.execute(input_data)

    # Should have results from successful aggregator
    assert len(result.results) == 1

    # Should track both failed searches
    assert len(result.failed_searches) == 2
    failed_names = {f.aggregator_name for f in result.failed_searches}
    assert "ThePirateBay" in failed_names
    assert "RARBG" in failed_names

    # Verify error messages have specific prefixes
    failed_dict = {f.aggregator_name: f.error_message for f in result.failed_searches}
    assert failed_dict["ThePirateBay"].startswith("Search failed:")
    assert "TPB failed" in failed_dict["ThePirateBay"]
    assert failed_dict["RARBG"].startswith("Search timed out:")
    assert "RARBG timeout" in failed_dict["RARBG"]


def test_search_torrents_no_failed_searches_when_all_succeed() -> None:
    """Should have empty failed_searches when all aggregators succeed."""
    query = "test"

    result = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Result",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service = Mock()
    mock_service.source = AggregatorSource.from_string("1337x")
    mock_service.search.return_value = [result]

    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_service.return_value = mock_service
    mock_registry.get_all_names.return_value = ["1337x"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query=query)

    result = use_case.execute(input_data)

    # Should have results
    assert len(result.results) == 1

    # Should have no failed searches
    assert len(result.failed_searches) == 0


def test_search_torrents_raises_error_for_empty_query() -> None:
    """Should raise ValidationError for empty query."""
    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_all_names.return_value = ["1337x"]
    mock_prefs_repo = Mock()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query="")

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "query" in str(exc_info.value).lower()
    assert "empty" in str(exc_info.value).lower()


def test_search_torrents_raises_error_for_invalid_max_results() -> None:
    """Should raise ValidationError for invalid max_results."""
    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_all_names.return_value = ["1337x"]
    mock_prefs_repo = Mock()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query="test", max_results=0)

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "max_results" in str(exc_info.value).lower()


def test_search_torrents_raises_error_for_invalid_aggregator_name() -> None:
    """Should raise ValidationError for invalid aggregator name."""
    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]
    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query="test", aggregator_names=["InvalidAggregator"]
    )

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "Invalid aggregator names" in str(exc_info.value)
    assert "InvalidAggregator" in str(exc_info.value)
    assert "Valid aggregators are" in str(exc_info.value)


def test_search_torrents_raises_error_for_multiple_invalid_aggregator_names() -> None:
    """Should raise ValidationError listing all invalid aggregator names."""
    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]
    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query="test", aggregator_names=["Invalid1", "Invalid2"]
    )

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    error_message = str(exc_info.value)
    assert "Invalid aggregator names" in error_message
    assert "Invalid1" in error_message
    assert "Invalid2" in error_message


def test_search_torrents_raises_error_for_mix_of_valid_and_invalid() -> None:
    """Should raise ValidationError even if some aggregator names are valid."""
    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]
    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query="test", aggregator_names=["1337x", "InvalidAggregator"]
    )

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "Invalid aggregator names" in str(exc_info.value)
    assert "InvalidAggregator" in str(exc_info.value)


def test_search_torrents_raises_error_for_empty_aggregator_list() -> None:
    """Should raise ValidationError for empty aggregator list."""
    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_all_names.return_value = ["1337x"]
    mock_prefs_repo = Mock()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query="test", aggregator_names=[])

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(input_data)

    assert "must contain at least one aggregator name" in str(exc_info.value)


def test_search_torrents_raises_error_when_no_aggregators_available() -> None:
    """Should raise AggregatorError when no aggregators available."""
    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_all_names.return_value = []
    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query="test")

    with pytest.raises(AggregatorError) as exc_info:
        use_case.execute(input_data)

    assert "No aggregators available" in str(exc_info.value)


def test_search_torrents_sorts_by_seeders_descending() -> None:
    """Should sort results by seeders in descending order."""
    query = "test"

    result1 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Low Seeders",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=10,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    result2 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "b" * 40),
        title="High Seeders",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=100,
        leechers=8,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    result3 = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "c" * 40),
        title="Medium Seeders",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=6,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service = Mock()
    mock_service.source = AggregatorSource.from_string("1337x")
    mock_service.search.return_value = [result1, result2, result3]

    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_service.return_value = mock_service
    mock_registry.get_all_names.return_value = ["1337x"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query=query)

    result = use_case.execute(input_data)

    assert len(result.results) == 3
    assert result.results[0].seeders == 100
    assert result.results[1].seeders == 50
    assert result.results[2].seeders == 10


def test_search_torrents_handles_timeout_error() -> None:
    """Should handle AggregatorTimeoutError and track it."""
    query = "test"

    result = TorrentSearchResult(
        magnet_link=MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40),
        title="Result",
        size=FileSize.from_bytes(1024 * 1024),
        seeders=50,
        leechers=5,
        source=AggregatorSource.from_string("1337x"),
        date_found=datetime(2025, 1, 1, 12, 0, 0),
    )

    mock_service1 = Mock()
    mock_service1.source = AggregatorSource.from_string("1337x")
    mock_service1.search.return_value = [result]

    mock_service2 = Mock()
    mock_service2.source = AggregatorSource.from_string("ThePirateBay")
    mock_service2.search.side_effect = AggregatorTimeoutError("Search timed out")

    mock_registry = Mock(spec=IAggregatorServiceRegistry)

    def get_service(name: str) -> Mock | None:
        if name == "1337x":
            return mock_service1
        if name == "ThePirateBay":
            return mock_service2
        return None

    mock_registry.get_service.side_effect = get_service
    mock_registry.get_all_names.return_value = ["1337x", "ThePirateBay"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(
        query=query, aggregator_names=["1337x", "ThePirateBay"]
    )

    result = use_case.execute(input_data)

    # Should still return results from successful aggregator
    assert len(result.results) == 1
    assert result.results[0].title == "Result"

    # Should track timeout error with specific message
    assert len(result.failed_searches) == 1
    assert result.failed_searches[0].aggregator_name == "ThePirateBay"
    assert result.failed_searches[0].error_message.startswith("Search timed out:")
    assert "Search timed out" in result.failed_searches[0].error_message


def test_search_torrents_propagates_non_aggregator_exceptions() -> None:
    """Should propagate non-AggregatorError exceptions."""
    query = "test"

    mock_service = Mock()
    mock_service.source = AggregatorSource.from_string("1337x")
    # Raise a non-AggregatorError exception
    mock_service.search.side_effect = ValueError("Unexpected error")

    mock_registry = Mock(spec=IAggregatorServiceRegistry)
    mock_registry.get_service.return_value = mock_service
    mock_registry.get_all_names.return_value = ["1337x"]

    mock_prefs_repo = Mock()
    mock_prefs_repo.get.return_value = UserPreferences.create_default()

    use_case = SearchTorrents(
        aggregator_service_registry=mock_registry,
        preferences_repository=mock_prefs_repo,
    )

    input_data = SearchTorrents.Input(query=query)

    # Should propagate the ValueError, not catch it
    with pytest.raises(ValueError) as exc_info:
        use_case.execute(input_data)

    assert "Unexpected error" in str(exc_info.value)


def test_to_dto_converts_correctly() -> None:
    """Should convert TorrentSearchResult entity to DTO correctly."""
    magnet_link = MagnetLink.from_string("magnet:?xt=urn:btih:" + "a" * 40)
    size = FileSize.from_bytes(1024 * 1024)
    source = AggregatorSource.from_string("1337x")
    date_found = datetime(2025, 1, 1, 12, 0, 0)

    result = TorrentSearchResult(
        magnet_link=magnet_link,
        title="Test Result",
        size=size,
        seeders=50,
        leechers=10,
        source=source,
        date_found=date_found,
    )

    dto = SearchTorrents._to_dto(result)

    assert dto.magnet_link == str(magnet_link)
    assert dto.title == "Test Result"
    assert dto.size == str(size)
    assert dto.seeders == 50
    assert dto.leechers == 10
    assert dto.source == str(source)
    assert dto.date_found == date_found
