"""Aggregator source value object."""

from dataclasses import dataclass

from nodo.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True, kw_only=True)
class AggregatorSource:
    """Represents the source aggregator/indexer where a torrent was found.

    Stores the aggregator name in a canonical format and provides
    case-insensitive comparison.

    Attributes:
        name: The aggregator name in canonical format.

    Example:
        >>> source1 = AggregatorSource.from_string("1337x")
        >>> source2 = AggregatorSource.from_string("1337X")
        >>> source1 == source2  # True
    """

    name: str

    _SUPPORTED_AGGREGATORS = {
        "1337x": "1337x",
        "thepiratebay": "ThePirateBay",
        "rarbg": "RARBG",
        "nyaa": "Nyaa",
        "torrentgalaxy": "TorrentGalaxy",
        "limetorrents": "LimeTorrents",
    }

    def __post_init__(self) -> None:
        """Validate the aggregator name."""
        if not self.name or not self.name.strip():
            raise ValidationError("Aggregator name cannot be empty")

    @classmethod
    def from_string(cls, name: str) -> "AggregatorSource":
        """Create an AggregatorSource from a string name.

        The name is normalized to canonical format if it matches
        a known aggregator (case-insensitive).

        Args:
            name: The aggregator name.

        Returns:
            An AggregatorSource instance with canonical name.

        Raises:
            ValidationError: If the name is empty.
        """
        if not name or not name.strip():
            raise ValidationError("Aggregator name cannot be empty")

        normalized = name.strip().lower()
        canonical = cls._SUPPORTED_AGGREGATORS.get(normalized, name.strip())

        return cls(name=canonical)

    @classmethod
    def get_supported_aggregators(cls) -> list[str]:
        """Get list of supported aggregator names in canonical format.

        Returns:
            List of supported aggregator names.
        """
        return list(cls._SUPPORTED_AGGREGATORS.values())

    @property
    def is_supported(self) -> bool:
        """Check if this aggregator is in the supported list.

        Returns:
            True if the aggregator is officially supported.
        """
        return self.name.lower() in self._SUPPORTED_AGGREGATORS

    def __str__(self) -> str:
        """Return the canonical name."""
        return self.name

    def __eq__(self, other: object) -> bool:
        """Case-insensitive equality comparison."""
        if not isinstance(other, AggregatorSource):
            return NotImplemented
        return self.name.lower() == other.name.lower()

    def __hash__(self) -> int:
        """Hash based on lowercase name for consistent hashing."""
        return hash(self.name.lower())
