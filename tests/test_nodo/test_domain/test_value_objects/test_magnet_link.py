"""Tests for TorrentLink value object (MagnetLink is a backward compatibility alias)."""

import pytest

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import MagnetLink, TorrentLink

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


def test_torrent_link_accept_http_url() -> None:
    """Should accept HTTP URLs."""
    uri = "http://example.com/torrent.torrent"
    link = TorrentLink(uri=uri)
    assert link.uri == uri


def test_torrent_link_accept_https_url() -> None:
    """Should accept HTTPS URLs."""
    uri = "https://example.com/torrent.torrent"
    link = TorrentLink(uri=uri)
    assert link.uri == uri


def test_torrent_link_reject_unsupported_scheme() -> None:
    """Should reject URIs with unsupported schemes."""
    with pytest.raises(ValidationError, match="Unsupported URL scheme"):
        TorrentLink(uri="ftp://example.com/torrent.torrent")


def test_torrent_link_reject_missing_scheme() -> None:
    """Should reject URIs without a scheme."""
    with pytest.raises(ValidationError, match="must be a valid URL with a scheme"):
        TorrentLink(uri="example.com/torrent.torrent")


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


def test_torrent_link_http_url_info_hash_is_none() -> None:
    """Info hash should be None for HTTP URLs."""
    link = TorrentLink(uri="http://example.com/torrent.torrent")
    assert link.info_hash is None


def test_torrent_link_https_url_info_hash_is_none() -> None:
    """Info hash should be None for HTTPS URLs."""
    link = TorrentLink(uri="https://example.com/torrent.torrent")
    assert link.info_hash is None


def test_magnet_link_without_valid_info_hash() -> None:
    """Should create magnet link but info_hash returns None if no valid hash found."""
    # This magnet link is valid from URL perspective but has no info hash
    uri = "magnet:?dn=Example"
    link = TorrentLink(uri=uri)
    assert link.uri == uri
    assert link.info_hash is None


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


def test_torrent_link_http_urls_equal_same_uri() -> None:
    """HTTP URLs with same URI should be equal."""
    uri = "http://example.com/torrent.torrent"
    link1 = TorrentLink(uri=uri)
    link2 = TorrentLink(uri=uri)
    assert link1 == link2


def test_torrent_link_http_urls_not_equal_different_uri() -> None:
    """HTTP URLs with different URIs should not be equal."""
    link1 = TorrentLink(uri="http://example.com/torrent1.torrent")
    link2 = TorrentLink(uri="http://example.com/torrent2.torrent")
    assert link1 != link2


def test_torrent_link_mixed_magnet_and_http_with_same_hash_not_equal() -> None:
    """Magnet link and HTTP URL should not be equal even if one has the hash."""
    magnet = TorrentLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    http = TorrentLink(uri="http://example.com/torrent.torrent")
    assert magnet != http


def test_torrent_link_two_http_links_same_hash_none() -> None:
    """Two HTTP links should be compared by URI, not by info_hash."""
    link1 = TorrentLink(uri="http://example.com/torrent.torrent")
    link2 = TorrentLink(uri="http://other.com/torrent.torrent")
    assert link1 != link2


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


def test_torrent_link_http_urls_hash_by_uri() -> None:
    """HTTP URLs should hash by full URI."""
    link1 = TorrentLink(uri="http://example.com/torrent.torrent")
    link2 = TorrentLink(uri="http://example.com/torrent.torrent")
    assert hash(link1) == hash(link2)


def test_torrent_link_mixed_in_set() -> None:
    """Both magnet links and HTTP URLs should be usable in sets."""
    magnet = TorrentLink(
        uri="magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678"
    )
    http1 = TorrentLink(uri="http://example.com/torrent1.torrent")
    http2 = TorrentLink(uri="http://example.com/torrent2.torrent")
    link_set = {magnet, http1, http2}
    assert len(link_set) == 3


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
