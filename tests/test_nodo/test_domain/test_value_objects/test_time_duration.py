"""Tests for TimeDuration value object."""

import pytest

from nodo.domain.exceptions import ValidationError
from nodo.domain.value_objects import TimeDuration


def test_time_duration_create_from_seconds() -> None:
    """Should create TimeDuration from seconds."""
    duration = TimeDuration.from_seconds(3600)
    assert duration.seconds == 3600


def test_time_duration_from_none_returns_none() -> None:
    """Should return None when creating from None."""
    assert TimeDuration.from_seconds(None) is None


def test_time_duration_is_immutable() -> None:
    """TimeDuration should be immutable (frozen)."""
    duration = TimeDuration.from_seconds(3600)
    assert duration is not None

    with pytest.raises(AttributeError):
        duration.seconds = 1800  # type: ignore[misc]


def test_time_duration_requires_keyword_arguments() -> None:
    """TimeDuration should require keyword arguments."""
    with pytest.raises(TypeError):
        TimeDuration(3600)  # type: ignore[misc]


def test_time_duration_raises_error_for_negative_seconds() -> None:
    """Should raise ValidationError for negative seconds."""
    with pytest.raises(ValidationError) as exc_info:
        TimeDuration.from_seconds(-1)

    assert "cannot be negative" in str(exc_info.value)


def test_time_duration_raises_error_for_too_large_seconds() -> None:
    """Should raise ValidationError for unreasonably large seconds."""
    max_reasonable = 100 * 365 * 24 * 60 * 60
    with pytest.raises(ValidationError) as exc_info:
        TimeDuration.from_seconds(max_reasonable + 1)

    assert "exceeds maximum reasonable value" in str(exc_info.value)


def test_time_duration_to_human_readable_zero() -> None:
    """Should format zero seconds correctly."""
    duration = TimeDuration.from_seconds(0)
    assert duration is not None
    assert duration.to_human_readable() == "0 seconds"


def test_time_duration_to_human_readable_seconds() -> None:
    """Should format seconds correctly."""
    assert TimeDuration.from_seconds(1).to_human_readable() == "1 second"
    assert TimeDuration.from_seconds(30).to_human_readable() == "30 seconds"
    assert TimeDuration.from_seconds(59).to_human_readable() == "59 seconds"


def test_time_duration_to_human_readable_minutes() -> None:
    """Should format minutes correctly."""
    assert TimeDuration.from_seconds(60).to_human_readable() == "1 minute"
    assert TimeDuration.from_seconds(120).to_human_readable() == "2 minutes"
    assert TimeDuration.from_seconds(3599).to_human_readable() == "59 minutes"


def test_time_duration_to_human_readable_hours() -> None:
    """Should format hours correctly."""
    assert TimeDuration.from_seconds(3600).to_human_readable() == "1 hour"
    assert TimeDuration.from_seconds(7200).to_human_readable() == "2 hours"
    assert TimeDuration.from_seconds(3660).to_human_readable() == "1 hour 1 minute"
    assert TimeDuration.from_seconds(3720).to_human_readable() == "1 hour 2 minutes"


def test_time_duration_to_human_readable_days() -> None:
    """Should format days correctly."""
    assert TimeDuration.from_seconds(86400).to_human_readable() == "1 day"
    assert TimeDuration.from_seconds(172800).to_human_readable() == "2 days"
    assert TimeDuration.from_seconds(90000).to_human_readable() == "1 day 1 hour"
    assert (
        TimeDuration.from_seconds(90060).to_human_readable() == "1 day 1 hour 1 minute"
    )
    assert TimeDuration.from_seconds(86460).to_human_readable() == "1 day 1 minute"
    assert TimeDuration.from_seconds(86520).to_human_readable() == "1 day 2 minutes"


def test_time_duration_str_returns_human_readable() -> None:
    """Should return human-readable format when converted to string."""
    duration = TimeDuration.from_seconds(3600)
    assert str(duration) == "1 hour"


def test_time_duration_comparison() -> None:
    """Should compare durations by seconds."""
    duration1 = TimeDuration.from_seconds(3600)
    duration2 = TimeDuration.from_seconds(7200)
    duration3 = TimeDuration.from_seconds(3600)

    assert duration1 < duration2
    assert duration2 > duration1
    assert duration1 <= duration2
    assert duration2 >= duration1
    assert duration1 <= duration3  # Equal case
    assert duration2 >= duration1  # Equal case
    assert duration1 == duration3
    assert duration1 != duration2


def test_time_duration_comparison_with_different_type() -> None:
    """Should raise TypeError when comparing with different type."""
    duration = TimeDuration.from_seconds(3600)
    with pytest.raises(TypeError):
        _ = duration < "not a duration"  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = duration > "not a duration"  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = duration <= "not a duration"  # type: ignore[operator]
    with pytest.raises(TypeError):
        _ = duration >= "not a duration"  # type: ignore[operator]
    assert (
        duration == "not a duration"
    ) is False  # __eq__ returns False, not TypeError


def test_time_duration_hashable() -> None:
    """TimeDuration should be hashable."""
    duration1 = TimeDuration.from_seconds(3600)
    duration2 = TimeDuration.from_seconds(3600)
    duration3 = TimeDuration.from_seconds(7200)

    assert hash(duration1) == hash(duration2)
    assert hash(duration1) != hash(duration3)

    # Should be usable in sets
    duration_set = {duration1, duration2, duration3}
    assert len(duration_set) == 2  # duration1 and duration2 are equal
