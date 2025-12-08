"""Tests for FileSize value object."""

import pytest

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import FileSize

# --- Creation and Validation ---


def test_file_size_create_with_zero_bytes() -> None:
    """Should create FileSize with zero bytes."""
    size = FileSize(bytes_=0)
    assert size.bytes_ == 0


def test_file_size_create_with_positive_bytes() -> None:
    """Should create FileSize with positive bytes."""
    size = FileSize(bytes_=1024)
    assert size.bytes_ == 1024


def test_file_size_from_bytes_factory() -> None:
    """Should create FileSize using from_bytes factory method."""
    size = FileSize.from_bytes(2048)
    assert size.bytes_ == 2048


def test_file_size_reject_negative_bytes() -> None:
    """Should reject negative byte count."""
    with pytest.raises(ValidationError, match="cannot be negative"):
        FileSize(bytes_=-1)


# --- Parsing from String ---


def test_file_size_parse_bytes() -> None:
    """Should parse bytes string."""
    size = FileSize.from_string("1024 B")
    assert size.bytes_ == 1024


def test_file_size_parse_kilobytes() -> None:
    """Should parse kilobytes string."""
    size = FileSize.from_string("1 KB")
    assert size.bytes_ == 1024


def test_file_size_parse_megabytes() -> None:
    """Should parse megabytes string."""
    size = FileSize.from_string("1 MB")
    assert size.bytes_ == 1024 * 1024


def test_file_size_parse_gigabytes() -> None:
    """Should parse gigabytes string."""
    size = FileSize.from_string("1 GB")
    assert size.bytes_ == 1024 * 1024 * 1024


def test_file_size_parse_terabytes() -> None:
    """Should parse terabytes string."""
    size = FileSize.from_string("1 TB")
    assert size.bytes_ == 1024 * 1024 * 1024 * 1024


def test_file_size_parse_decimal_value() -> None:
    """Should parse decimal values."""
    size = FileSize.from_string("1.5 GB")
    assert size.bytes_ == int(1.5 * 1024 * 1024 * 1024)


def test_file_size_parse_without_space() -> None:
    """Should parse value without space between number and unit."""
    size = FileSize.from_string("750MB")
    assert size.bytes_ == 750 * 1024 * 1024


def test_file_size_parse_case_insensitive() -> None:
    """Should parse units case-insensitively."""
    size1 = FileSize.from_string("1 gb")
    size2 = FileSize.from_string("1 GB")
    size3 = FileSize.from_string("1 Gb")
    assert size1.bytes_ == size2.bytes_ == size3.bytes_


def test_file_size_parse_with_whitespace() -> None:
    """Should parse values with leading/trailing whitespace."""
    size = FileSize.from_string("  500 MB  ")
    assert size.bytes_ == 500 * 1024 * 1024


def test_file_size_reject_invalid_format() -> None:
    """Should reject invalid format."""
    with pytest.raises(ValidationError, match="Invalid size format"):
        FileSize.from_string("not a size")


def test_file_size_reject_missing_unit() -> None:
    """Should reject value without unit."""
    with pytest.raises(ValidationError, match="Invalid size format"):
        FileSize.from_string("1024")


def test_file_size_reject_invalid_unit() -> None:
    """Should reject invalid unit."""
    with pytest.raises(ValidationError, match="Invalid size format"):
        FileSize.from_string("1024 XB")


# --- Human-Readable Formatting ---


def test_file_size_format_zero_bytes() -> None:
    """Should format zero bytes."""
    size = FileSize(bytes_=0)
    assert size.to_human_readable() == "0 B"


def test_file_size_format_bytes() -> None:
    """Should format small values as bytes."""
    size = FileSize(bytes_=512)
    assert size.to_human_readable() == "512 B"


def test_file_size_format_kilobytes() -> None:
    """Should format kilobyte values."""
    size = FileSize(bytes_=1536)  # 1.5 KB
    assert size.to_human_readable() == "1.50 KB"


def test_file_size_format_megabytes() -> None:
    """Should format megabyte values."""
    size = FileSize(bytes_=1572864)  # 1.5 MB
    assert size.to_human_readable() == "1.50 MB"


def test_file_size_format_gigabytes() -> None:
    """Should format gigabyte values."""
    size = FileSize(bytes_=1610612736)  # 1.5 GB
    assert size.to_human_readable() == "1.50 GB"


def test_file_size_format_terabytes() -> None:
    """Should format terabyte values."""
    size = FileSize(bytes_=1649267441664)  # 1.5 TB
    assert size.to_human_readable() == "1.50 TB"


def test_file_size_str_returns_human_readable() -> None:
    """str() should return human-readable format."""
    size = FileSize(bytes_=1024 * 1024)
    assert str(size) == "1.00 MB"


# --- Comparison Operations ---


def test_file_size_less_than() -> None:
    """Should compare sizes with less than."""
    small = FileSize(bytes_=1024)
    large = FileSize(bytes_=2048)
    assert small < large
    assert not large < small


def test_file_size_less_than_or_equal() -> None:
    """Should compare sizes with less than or equal."""
    small = FileSize(bytes_=1024)
    equal = FileSize(bytes_=1024)
    large = FileSize(bytes_=2048)
    assert small <= large
    assert small <= equal
    assert not large <= small


def test_file_size_greater_than() -> None:
    """Should compare sizes with greater than."""
    small = FileSize(bytes_=1024)
    large = FileSize(bytes_=2048)
    assert large > small
    assert not small > large


def test_file_size_greater_than_or_equal() -> None:
    """Should compare sizes with greater than or equal."""
    small = FileSize(bytes_=1024)
    equal = FileSize(bytes_=1024)
    large = FileSize(bytes_=2048)
    assert large >= small
    assert equal >= small
    assert not small >= large


def test_file_size_equality() -> None:
    """Should compare sizes for equality."""
    size1 = FileSize(bytes_=1024)
    size2 = FileSize(bytes_=1024)
    size3 = FileSize(bytes_=2048)
    assert size1 == size2
    assert size1 != size3


def test_file_size_comparison_with_non_file_size_returns_not_implemented() -> None:
    """Comparison with non-FileSize should return NotImplemented."""
    size = FileSize(bytes_=1024)
    assert size.__lt__("not a size") == NotImplemented
    assert size.__le__("not a size") == NotImplemented
    assert size.__gt__("not a size") == NotImplemented
    assert size.__ge__("not a size") == NotImplemented
    assert size.__eq__("not a size") == NotImplemented


# --- Hashing ---


def test_file_size_equal_sizes_have_same_hash() -> None:
    """Equal sizes should have the same hash."""
    size1 = FileSize(bytes_=1024)
    size2 = FileSize(bytes_=1024)
    assert hash(size1) == hash(size2)


def test_file_size_usable_in_set() -> None:
    """FileSize should be usable in sets."""
    size_set = {FileSize(bytes_=1024), FileSize(bytes_=1024), FileSize(bytes_=2048)}
    assert len(size_set) == 2


# --- Immutability ---


def test_file_size_cannot_modify_bytes() -> None:
    """Should not be able to modify bytes_ attribute."""
    size = FileSize(bytes_=1024)
    with pytest.raises(AttributeError):
        size.bytes_ = 2048  # type: ignore[misc]
