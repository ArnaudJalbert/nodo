"""Torrent link value object."""

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from nodo.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True, kw_only=True)
class TorrentLink:
    """Represents a torrent link in various formats.

    Supports multiple URL schemes for accessing torrents:
    - magnet: URIs (magnet:?xt=urn:btih:...)
    - HTTP/HTTPS URLs (.torrent file downloads)
    - Other URI schemes with valid torrent identifiers

    The info_hash property is only available for magnet links.
    For HTTP/HTTPS URLs, info_hash returns None.

    Attributes:
        uri: The full torrent link URI.

    Examples:
        >>> magnet = TorrentLink.from_string("magnet:?xt=urn:btih:abc123...")
        >>> info_hash = magnet.info_hash
        >>> http_link = TorrentLink.from_string("https://example.com/torrent.torrent")
        >>> http_link.info_hash  # None for HTTP URLs
    """

    uri: str

    _INFO_HASH_PATTERN = re.compile(r"xt=urn:btih:([a-fA-F0-9]{64}|[a-fA-F0-9]{40})")

    def __post_init__(self) -> None:
        """Validate the torrent link format."""
        parsed = urlparse(self.uri)
        if not parsed.scheme:
            raise ValidationError(
                "Link must be a valid URL with a scheme (magnet, http, or https)"
            )

        if parsed.scheme not in ("magnet", "http", "https"):
            raise ValidationError(
                f"Unsupported URL scheme '{parsed.scheme}'. "
                "Link must use magnet, http, or https scheme"
            )

    @classmethod
    def from_string(cls, uri: str) -> "TorrentLink":
        """Create a TorrentLink from a string URI.

        Args:
            uri: The torrent link URI string (magnet:, http:, or https:).

        Returns:
            A validated TorrentLink instance.

        Raises:
            ValidationError: If the URI is not a valid torrent link.
        """
        return cls(uri=uri)

    @property
    def info_hash(self) -> str | None:
        """Extract the torrent info hash from the link.

        Only available for magnet links. Returns None for HTTP/HTTPS URLs.

        Returns:
            The info hash (40 or 64 character hexadecimal string) for magnet links,
            or None for other URL types.
        """
        if self.uri.startswith("magnet:"):
            match = self._INFO_HASH_PATTERN.search(self.uri)
            return match.group(1).lower() if match else None
        return None

    def __str__(self) -> str:
        """Return the full torrent URI."""
        return self.uri

    def __eq__(self, other: object) -> bool:
        """Compare two torrent links for equality.

        If both links have info_hash values (magnet links), comparison is based
        on info_hash. Otherwise, comparison is based on the full URI.
        """
        if not isinstance(other, TorrentLink):
            return NotImplemented
        # If both have info_hash, compare by that
        if self.info_hash and other.info_hash:
            return self.info_hash == other.info_hash
        # Otherwise compare full URIs
        return self.uri == other.uri

    def __hash__(self) -> int:
        """Hash for use in sets and dicts.

        For magnet links with info_hash, hashes the info_hash.
        For other URLs, hashes the full URI.
        """
        if self.info_hash:
            return hash(self.info_hash)
        return hash(self.uri)


# Backward compatibility alias
MagnetLink = TorrentLink
