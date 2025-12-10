"""Tests for AggregatorSource value object."""

import pytest

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import AggregatorSource

# --- Creation and Validation ---


def test_aggregator_source_create_with_valid_name() -> None:
    """Should create AggregatorSource with valid name."""
    source = AggregatorSource(name="1337x")
    assert source.name == "1337x"


def test_aggregator_source_from_string_factory() -> None:
    """Should create AggregatorSource using from_string factory method."""
    source = AggregatorSource.from_string("1337x")
    assert source.name == "1337x"


def test_aggregator_source_from_string_normalizes_known_aggregator() -> None:
    """Should normalize known aggregator names to canonical format."""
    source = AggregatorSource.from_string("thepiratebay")
    assert source.name == "ThePirateBay"


def test_aggregator_source_from_string_preserves_unknown_aggregator() -> None:
    """Should preserve unknown aggregator names as provided."""
    source = AggregatorSource.from_string("CustomAggregator")
    assert source.name == "CustomAggregator"


def test_aggregator_source_from_string_strips_whitespace() -> None:
    """Should strip whitespace from aggregator name."""
    source = AggregatorSource.from_string("  1337x  ")
    assert source.name == "1337x"


def test_aggregator_source_reject_empty_name() -> None:
    """Should reject empty aggregator name."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        AggregatorSource(name="")


def test_aggregator_source_reject_whitespace_only_name() -> None:
    """Should reject whitespace-only aggregator name."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        AggregatorSource.from_string("   ")


# --- Supported Aggregators ---


def test_aggregator_source_get_supported_aggregators() -> None:
    """Should return list of supported aggregators."""
    supported = AggregatorSource.get_supported_aggregators()
    assert "1337x" in supported
    assert "ThePirateBay" in supported
    assert "RARBG" in supported
    assert "Nyaa" in supported
    assert "TorrentGalaxy" in supported
    assert "LimeTorrents" in supported


def test_aggregator_source_is_supported_for_known_aggregator() -> None:
    """Should return True for known aggregators."""
    source = AggregatorSource.from_string("1337x")
    assert source.is_supported is True


def test_aggregator_source_is_supported_for_unknown_aggregator() -> None:
    """Should return False for unknown aggregators."""
    source = AggregatorSource.from_string("UnknownAggregator")
    assert source.is_supported is False


# --- Equality and Hashing ---


def test_aggregator_source_equal_when_same_name() -> None:
    """Aggregator sources with same name should be equal."""
    source1 = AggregatorSource(name="1337x")
    source2 = AggregatorSource(name="1337x")
    assert source1 == source2


def test_aggregator_source_equal_case_insensitive() -> None:
    """Aggregator sources should be compared case-insensitively."""
    source1 = AggregatorSource(name="ThePirateBay")
    source2 = AggregatorSource(name="thepiratebay")
    assert source1 == source2


def test_aggregator_source_not_equal_when_different_name() -> None:
    """Aggregator sources with different names should not be equal."""
    source1 = AggregatorSource(name="1337x")
    source2 = AggregatorSource(name="RARBG")
    assert source1 != source2


def test_aggregator_source_not_equal_to_non_aggregator_source() -> None:
    """AggregatorSource should not be equal to non-AggregatorSource objects."""
    source = AggregatorSource(name="1337x")
    assert source.__eq__("1337x") == NotImplemented
    assert source.__eq__(123) == NotImplemented


def test_aggregator_source_hash_equal_for_equal_sources() -> None:
    """Equal aggregator sources should have same hash."""
    source1 = AggregatorSource(name="ThePirateBay")
    source2 = AggregatorSource(name="thepiratebay")
    assert hash(source1) == hash(source2)


def test_aggregator_source_usable_in_set() -> None:
    """AggregatorSource should be usable in sets."""
    source_set = {
        AggregatorSource(name="1337x"),
        AggregatorSource(name="1337X"),
        AggregatorSource(name="RARBG"),
    }
    assert len(source_set) == 2


# --- String Representation ---


def test_aggregator_source_str_returns_name() -> None:
    """str() should return the canonical name."""
    source = AggregatorSource.from_string("thepiratebay")
    assert str(source) == "ThePirateBay"


# --- Immutability ---


def test_aggregator_source_cannot_modify_name() -> None:
    """Should not be able to modify name attribute."""
    source = AggregatorSource(name="1337x")
    with pytest.raises(AttributeError):
        source.name = "RARBG"  # type: ignore[misc]
