"""Tests for IndexerSource value object."""

import pytest

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import IndexerSource

# --- Creation and Validation ---


def test_indexer_source_create_with_valid_name() -> None:
    """Should create IndexerSource with valid name."""
    source = IndexerSource(name="Prowlarr")
    assert source.name == "Prowlarr"


def test_indexer_source_from_string_factory() -> None:
    """Should create IndexerSource using from_string factory method."""
    source = IndexerSource.from_string("Prowlarr")
    assert source.name == "Prowlarr"


def test_indexer_source_from_string_normalizes_known_indexer() -> None:
    """Should normalize known indexer names to canonical format."""
    source = IndexerSource.from_string("prowlarr")
    assert source.name == "Prowlarr"


def test_indexer_source_from_string_preserves_unknown_indexer() -> None:
    """Should preserve unknown indexer names as provided."""
    source = IndexerSource.from_string("CustomIndexer")
    assert source.name == "CustomIndexer"


def test_indexer_source_from_string_strips_whitespace() -> None:
    """Should strip whitespace from indexer name."""
    source = IndexerSource.from_string("  Prowlarr  ")
    assert source.name == "Prowlarr"


def test_indexer_source_reject_empty_name() -> None:
    """Should reject empty indexer name."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        IndexerSource(name="")


def test_indexer_source_reject_whitespace_only_name() -> None:
    """Should reject whitespace-only indexer name."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        IndexerSource.from_string("   ")


# --- Supported Indexers ---


def test_indexer_source_get_supported_indexers() -> None:
    """Should return list of supported indexers."""
    supported = IndexerSource.get_supported_indexers()
    assert "Prowlarr" in supported
    assert len(supported) == 1


def test_indexer_source_is_supported_for_known_indexer() -> None:
    """Should return True for known indexers."""
    source = IndexerSource.from_string("Prowlarr")
    assert source.is_supported is True


def test_indexer_source_is_supported_for_unknown_indexer() -> None:
    """Should return False for unknown indexers."""
    source = IndexerSource.from_string("UnknownIndexer")
    assert source.is_supported is False


# --- Equality and Hashing ---


def test_indexer_source_equal_when_same_name() -> None:
    """Indexer sources with same name should be equal."""
    source1 = IndexerSource(name="Prowlarr")
    source2 = IndexerSource(name="Prowlarr")
    assert source1 == source2


def test_indexer_source_equal_case_insensitive() -> None:
    """Indexer sources should be compared case-insensitively."""
    source1 = IndexerSource(name="Prowlarr")
    source2 = IndexerSource(name="prowlarr")
    assert source1 == source2


def test_indexer_source_not_equal_when_different_name() -> None:
    """Indexer sources with different names should not be equal."""
    source1 = IndexerSource(name="Prowlarr")
    source2 = IndexerSource(name="CustomIndexer")
    assert source1 != source2


def test_indexer_source_not_equal_to_non_indexer_source() -> None:
    """IndexerSource should not be equal to non-IndexerSource objects."""
    source = IndexerSource(name="Prowlarr")
    assert source.__eq__("Prowlarr") == NotImplemented
    assert source.__eq__(123) == NotImplemented


def test_indexer_source_hash_equal_for_equal_sources() -> None:
    """Equal indexer sources should have same hash."""
    source1 = IndexerSource(name="Prowlarr")
    source2 = IndexerSource(name="prowlarr")
    assert hash(source1) == hash(source2)


def test_indexer_source_usable_in_set() -> None:
    """IndexerSource should be usable in sets."""
    source_set = {
        IndexerSource(name="Prowlarr"),
        IndexerSource(name="prowlarr"),
        IndexerSource(name="CustomIndexer"),
    }
    # Prowlarr and prowlarr are the same (case-insensitive), so only 2 unique
    assert len(source_set) == 2


# --- String Representation ---


def test_indexer_source_str_returns_name() -> None:
    """str() should return the canonical name."""
    source = IndexerSource.from_string("prowlarr")
    assert str(source) == "Prowlarr"


# --- Immutability ---


def test_indexer_source_cannot_modify_name() -> None:
    """Should not be able to modify name attribute."""
    source = IndexerSource(name="Prowlarr")
    with pytest.raises(AttributeError):
        source.name = "Prowlarr"  # type: ignore[misc]
