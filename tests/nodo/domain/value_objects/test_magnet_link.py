"""Tests for MagnetLink value object."""

import pytest

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import MagnetLink

# --- Creation and Validation ---


def test_magnet_link_create_with_valid_sha1_hash() -> None:
    """Should create MagnetLink with valid SHA-1 info hash."""
    uri = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    magnet = MagnetLink(uri=uri)
    assert magnet.uri == uri


def test_magnet_link_create_with_valid_sha256_hash() -> None:
    """Should create MagnetLink with valid SHA-256 info hash."""
    uri = (
        "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef"
        "1234567890abcdef1234567890abcdef"
    )
    magnet = MagnetLink(uri=uri)
    assert magnet.uri == uri


def test_magnet_link_create_with_additional_parameters() -> None:
    """Should create MagnetLink with additional parameters like trackers."""
    uri = (
        "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
        "&dn=Example+Torrent&tr=udp://tracker.example.com:80"
    )
    magnet = MagnetLink(uri=uri)
    assert magnet.uri == uri


def test_magnet_link_from_string_factory() -> None:
    """Should create MagnetLink using from_string factory method."""
    uri = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    magnet = MagnetLink.from_string(uri)
    assert magnet.uri == uri


def test_magnet_link_reject_without_magnet_prefix() -> None:
    """Should reject URI that doesn't start with magnet:?"""
    with pytest.raises(ValidationError, match="must start with 'magnet:\\?'"):
        MagnetLink(uri="http://example.com")


def test_magnet_link_reject_without_info_hash() -> None:
    """Should reject URI without valid info hash."""
    with pytest.raises(ValidationError, match="must contain a valid info hash"):
        MagnetLink(uri="magnet:?dn=Example")


def test_magnet_link_reject_short_info_hash() -> None:
    """Should reject URI with info hash shorter than 40 characters."""
    with pytest.raises(ValidationError, match="must contain a valid info hash"):
        MagnetLink(uri="magnet:?xt=urn:btih:123456789")


def test_magnet_link_reject_invalid_info_hash_characters() -> None:
    """Should reject URI with non-hexadecimal info hash."""
    with pytest.raises(ValidationError, match="must contain a valid info hash"):
        MagnetLink(uri="magnet:?xt=urn:btih:zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")


# --- Info Hash Extraction ---


def test_magnet_link_extract_sha1_info_hash() -> None:
    """Should extract SHA-1 info hash from magnet link."""
    uri = "magnet:?xt=urn:btih:1234567890ABCDEF1234567890abcdef12345678"
    magnet = MagnetLink(uri=uri)
    assert magnet.info_hash == "1234567890abcdef1234567890abcdef12345678"


def test_magnet_link_extract_sha256_info_hash() -> None:
    """Should extract SHA-256 info hash from magnet link."""
    uri = (
        "magnet:?xt=urn:btih:1234567890ABCDEF1234567890abcdef"
        "1234567890ABCDEF1234567890abcdef"
    )
    magnet = MagnetLink(uri=uri)
    assert (
        magnet.info_hash
        == "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )


def test_magnet_link_info_hash_is_lowercase() -> None:
    """Info hash should be normalized to lowercase."""
    uri = "magnet:?xt=urn:btih:ABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCD"
    magnet = MagnetLink(uri=uri)
    assert magnet.info_hash == "abcdefabcdefabcdefabcdefabcdefabcdefabcd"


# --- Equality and Hashing ---


def test_magnet_link_equal_when_same_info_hash() -> None:
    """Magnet links with same info hash should be equal."""
    uri1 = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    uri2 = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678&dn=Different"
    magnet1 = MagnetLink(uri=uri1)
    magnet2 = MagnetLink(uri=uri2)
    assert magnet1 == magnet2


def test_magnet_link_equal_with_different_case_info_hash() -> None:
    """Magnet links with same info hash in different case should be equal."""
    uri1 = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    uri2 = "magnet:?xt=urn:btih:1234567890ABCDEF1234567890ABCDEF12345678"
    magnet1 = MagnetLink(uri=uri1)
    magnet2 = MagnetLink(uri=uri2)
    assert magnet1 == magnet2


def test_magnet_link_not_equal_when_different_info_hash() -> None:
    """Magnet links with different info hashes should not be equal."""
    uri1 = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    uri2 = "magnet:?xt=urn:btih:abcdef1234567890abcdef1234567890abcdef12"
    magnet1 = MagnetLink(uri=uri1)
    magnet2 = MagnetLink(uri=uri2)
    assert magnet1 != magnet2


def test_magnet_link_not_equal_to_non_magnet_link() -> None:
    """MagnetLink should not be equal to non-MagnetLink objects."""
    uri = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    magnet = MagnetLink(uri=uri)
    assert magnet.__eq__("not a magnet link") == NotImplemented
    assert magnet.__eq__(123) == NotImplemented


def test_magnet_link_hash_equal_for_equal_magnets() -> None:
    """Equal magnet links should have same hash."""
    uri1 = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    uri2 = "magnet:?xt=urn:btih:1234567890ABCDEF1234567890ABCDEF12345678"
    magnet1 = MagnetLink(uri=uri1)
    magnet2 = MagnetLink(uri=uri2)
    assert hash(magnet1) == hash(magnet2)


def test_magnet_link_usable_in_set() -> None:
    """MagnetLink should be usable in sets."""
    uri1 = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    uri2 = "magnet:?xt=urn:btih:1234567890ABCDEF1234567890ABCDEF12345678"
    uri3 = "magnet:?xt=urn:btih:abcdef1234567890abcdef1234567890abcdef12"
    magnet_set = {MagnetLink(uri=uri1), MagnetLink(uri=uri2), MagnetLink(uri=uri3)}
    assert len(magnet_set) == 2


# --- Immutability ---


def test_magnet_link_cannot_modify_uri() -> None:
    """Should not be able to modify uri attribute."""
    magnet = MagnetLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    with pytest.raises(AttributeError):
        magnet.uri = "magnet:?xt=urn:btih:abcdef1234567890abcdef1234567890abcdef12"  # type: ignore[misc]


# --- String Representation ---


def test_magnet_link_str_returns_uri() -> None:
    """str() should return the full magnet URI."""
    uri = "magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    magnet = MagnetLink(uri=uri)
    assert str(magnet) == uri
