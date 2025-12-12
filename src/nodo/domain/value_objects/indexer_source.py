"""Indexer source value object."""

from dataclasses import dataclass

from nodo.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True, kw_only=True)
class IndexerSource:
    """Represents the source indexer where a torrent was found.

    Stores the indexer name in a canonical format and provides
    case-insensitive comparison.

    Attributes:
        name: The indexer name in canonical format.

    Example:
        >>> source1 = IndexerSource.from_string("Prowlarr")
        >>> source2 = IndexerSource.from_string("prowlarr")
        >>> source1 == source2  # True
    """

    name: str

    _SUPPORTED_INDEXERS = {
        "prowlarr": "Prowlarr",
    }

    def __post_init__(self) -> None:
        """Validate the indexer name."""
        if not self.name or not self.name.strip():
            raise ValidationError("Indexer name cannot be empty")

    @classmethod
    def from_string(cls, name: str) -> "IndexerSource":
        """Create an IndexerSource from a string name.

        The name is normalized to canonical format if it matches
        a known indexer (case-insensitive).

        Args:
            name: The indexer name.

        Returns:
            An IndexerSource instance with canonical name.

        Raises:
            ValidationError: If the name is empty.
        """
        if not name or not name.strip():
            raise ValidationError("Indexer name cannot be empty")

        normalized = name.strip().lower()
        canonical = cls._SUPPORTED_INDEXERS.get(normalized, name.strip())

        return cls(name=canonical)

    @classmethod
    def get_supported_indexers(cls) -> list[str]:
        """Get list of supported indexer names in canonical format.

        Returns:
            List of supported indexer names.
        """
        return list(cls._SUPPORTED_INDEXERS.values())

    @property
    def is_supported(self) -> bool:
        """Check if this indexer is in the supported list.

        Returns:
            True if the indexer is officially supported.
        """
        return self.name.lower() in self._SUPPORTED_INDEXERS

    def __str__(self) -> str:
        """Return the canonical name."""
        return self.name

    def __eq__(self, other: object) -> bool:
        """Case-insensitive equality comparison."""
        if not isinstance(other, IndexerSource):
            return NotImplemented
        return self.name.lower() == other.name.lower()

    def __hash__(self) -> int:
        """Hash based on lowercase name for consistent hashing."""
        return hash(self.name.lower())
