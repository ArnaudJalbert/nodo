"""Magnet link value object."""

import re
from dataclasses import dataclass

from nodo.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True, kw_only=True)
class MagnetLink:
    """Represents a magnet URI for BitTorrent downloads.

    A magnet link is a URI scheme that allows users to download files
    through peer-to-peer networks using a unique identifier (info hash)
    rather than a specific server location.

    Attributes:
        uri: The full magnet link URI.

    Example:
        >>> magnet = MagnetLink.from_string("magnet:?xt=urn:btih:abc123...")
        >>> info_hash = magnet.info_hash
    """

    uri: str

    _INFO_HASH_PATTERN = re.compile(r"xt=urn:btih:([a-fA-F0-9]{64}|[a-fA-F0-9]{40})")

    def __post_init__(self) -> None:
        """Validate the magnet link format."""
        if not self.uri.startswith("magnet:?"):
            raise ValidationError("Magnet link must start with 'magnet:?'")

        if not self._INFO_HASH_PATTERN.search(self.uri):
            raise ValidationError(
                "Magnet link must contain a valid info hash "
                "(40 character SHA-1 or 64 character SHA-256)"
            )

    @classmethod
    def from_string(cls, uri: str) -> "MagnetLink":
        """Create a MagnetLink from a string URI.

        Args:
            uri: The magnet link URI string.

        Returns:
            A validated MagnetLink instance.

        Raises:
            ValidationError: If the URI is not a valid magnet link.
        """
        return cls(uri=uri)

    @property
    def info_hash(self) -> str:
        """Extract the torrent info hash from the magnet link.

        Returns:
            The info hash (40 or 64 character hexadecimal string).
        """
        match = self._INFO_HASH_PATTERN.search(self.uri)
        # Safe to assert since __post_init__ validates this
        assert match is not None
        return match.group(1).lower()

    def __str__(self) -> str:
        """Return the full magnet URI."""
        return self.uri

    def __eq__(self, other: object) -> bool:
        """Two magnet links are equal if their info hashes match."""
        if not isinstance(other, MagnetLink):
            return NotImplemented
        return self.info_hash == other.info_hash

    def __hash__(self) -> int:
        """Hash based on info hash for use in sets and dicts."""
        return hash(self.info_hash)
