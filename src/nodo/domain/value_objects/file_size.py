"""File size value object."""

import re
from dataclasses import dataclass

from nodo.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True, kw_only=True)
class FileSize:
    """Represents the size of a file with human-readable formatting.

    Stores size internally as bytes for precision and provides
    methods for human-readable display and parsing.

    Attributes:
        bytes_: Size in bytes (canonical representation).

    Example:
        >>> size = FileSize.from_bytes(1_500_000_000)
        >>> print(size)  # "1.40 GB"
        >>> size2 = FileSize.from_string("750 MB")
        >>> size > size2  # True
    """

    bytes_: int

    _UNITS = ["B", "KB", "MB", "GB", "TB"]
    _UNIT_MULTIPLIERS = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
    }
    _SIZE_PATTERN = re.compile(r"^\s*([\d.]+)\s*(B|KB|MB|GB|TB)\s*$", re.IGNORECASE)

    def __post_init__(self) -> None:
        """Validate the byte count."""
        if self.bytes_ < 0:
            raise ValidationError("File size cannot be negative")

    @classmethod
    def from_bytes(cls, size: int) -> "FileSize":
        """Create a FileSize from a byte count.

        Args:
            size: Size in bytes.

        Returns:
            A FileSize instance.

        Raises:
            ValidationError: If size is negative.
        """
        return cls(bytes_=size)

    @classmethod
    def from_string(cls, size: str) -> "FileSize":
        """Parse a FileSize from a human-readable string.

        Supports formats like "1.5 GB", "750MB", "1024 KB".

        Args:
            size: Human-readable size string.

        Returns:
            A FileSize instance.

        Raises:
            ValidationError: If the string format is invalid.
        """
        match = cls._SIZE_PATTERN.match(size)
        if not match:
            raise ValidationError(
                f"Invalid size format: '{size}'. "
                f"Expected format like '1.5 GB' or '750 MB'"
            )

        value = float(match.group(1))
        unit = match.group(2).upper()
        bytes_count = int(value * cls._UNIT_MULTIPLIERS[unit])

        return cls(bytes_=bytes_count)

    def to_human_readable(self) -> str:
        """Convert to human-readable format with appropriate unit.

        Uses binary units (1 KB = 1024 bytes) and rounds to 2 decimal places.

        Returns:
            Human-readable size string (e.g., "1.40 GB").
        """
        if self.bytes_ == 0:
            return "0 B"

        size = float(self.bytes_)
        unit = "B"
        for unit in self._UNITS:
            if size < 1024 or unit == "TB":
                break
            size /= 1024

        if unit == "B":
            return f"{int(size)} B"
        return f"{size:.2f} {unit}"

    def __str__(self) -> str:
        """Return human-readable format."""
        return self.to_human_readable()

    def __lt__(self, other: object) -> bool:
        """Compare sizes by byte value."""
        if not isinstance(other, FileSize):
            return NotImplemented
        return self.bytes_ < other.bytes_

    def __le__(self, other: object) -> bool:
        """Compare sizes by byte value."""
        if not isinstance(other, FileSize):
            return NotImplemented
        return self.bytes_ <= other.bytes_

    def __gt__(self, other: object) -> bool:
        """Compare sizes by byte value."""
        if not isinstance(other, FileSize):
            return NotImplemented
        return self.bytes_ > other.bytes_

    def __ge__(self, other: object) -> bool:
        """Compare sizes by byte value."""
        if not isinstance(other, FileSize):
            return NotImplemented
        return self.bytes_ >= other.bytes_

    def __eq__(self, other: object) -> bool:
        """Compare sizes by byte value."""
        if not isinstance(other, FileSize):
            return NotImplemented
        return self.bytes_ == other.bytes_

    def __hash__(self) -> int:
        """Hash based on byte value."""
        return hash(self.bytes_)
