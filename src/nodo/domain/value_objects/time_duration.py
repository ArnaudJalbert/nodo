"""Time duration value object."""

from dataclasses import dataclass

from nodo.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeDuration:
    """Represents a time duration with human-readable formatting.

    Stores duration internally as seconds for precision and provides
    methods for human-readable display.

    Attributes:
        seconds: Duration in seconds (canonical representation).

    Example:
        >>> duration = TimeDuration.from_seconds(3661)
        >>> print(duration)  # "1 hour 1 minute 1 second"
    """

    seconds: int

    # Max reasonable duration: 100 years in seconds
    _MAX_REASONABLE_SECONDS = 100 * 365 * 24 * 60 * 60

    def __post_init__(self) -> None:
        """Validate the duration."""
        if self.seconds < 0:
            raise ValidationError("Time duration cannot be negative")
        if self.seconds > self._MAX_REASONABLE_SECONDS:
            raise ValidationError(
                f"Time duration exceeds maximum reasonable value "
                f"({self._MAX_REASONABLE_SECONDS} seconds)"
            )

    @classmethod
    def from_seconds(cls, seconds: int | None) -> "TimeDuration | None":
        """Create a TimeDuration from seconds.

        Args:
            seconds: Duration in seconds, or None if unknown.

        Returns:
            A TimeDuration instance, or None if seconds is None.
        """
        if seconds is None:
            return None
        return cls(seconds=seconds)

    def to_human_readable(self) -> str:
        """Convert to human-readable format.

        Returns:
            Human-readable duration string (e.g., "1 hour 30 minutes").
        """
        if self.seconds == 0:
            return "0 seconds"

        if self.seconds < 60:
            return f"{self.seconds} second{'s' if self.seconds != 1 else ''}"

        minutes = self.seconds // 60

        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"

        hours = minutes // 60
        remaining_minutes = minutes % 60

        if hours < 24:
            hour_str = f"{hours} hour{'s' if hours != 1 else ''}"
            if remaining_minutes == 0:
                return hour_str
            minute_str = (
                f"{remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"
            )
            return f"{hour_str} {minute_str}"

        days = hours // 24
        remaining_hours = hours % 24
        remaining_minutes_after_days = minutes % 60

        day_str = f"{days} day{'s' if days != 1 else ''}"
        hour_str = f"{remaining_hours} hour{'s' if remaining_hours != 1 else ''}"
        minute_str = (
            f"{remaining_minutes_after_days} minute"
            f"{'s' if remaining_minutes_after_days != 1 else ''}"
        )

        if remaining_hours == 0 and remaining_minutes_after_days == 0:
            return day_str
        if remaining_hours == 0:
            return f"{day_str} {minute_str}"
        if remaining_minutes_after_days == 0:
            return f"{day_str} {hour_str}"
        return f"{day_str} {hour_str} {minute_str}"

    def __str__(self) -> str:
        """Return human-readable format."""
        return self.to_human_readable()

    def __lt__(self, other: object) -> bool:
        """Compare durations by seconds."""
        if not isinstance(other, TimeDuration):
            return NotImplemented
        return self.seconds < other.seconds

    def __le__(self, other: object) -> bool:
        """Compare durations by seconds."""
        if not isinstance(other, TimeDuration):
            return NotImplemented
        return self.seconds <= other.seconds

    def __gt__(self, other: object) -> bool:
        """Compare durations by seconds."""
        if not isinstance(other, TimeDuration):
            return NotImplemented
        return self.seconds > other.seconds

    def __ge__(self, other: object) -> bool:
        """Compare durations by seconds."""
        if not isinstance(other, TimeDuration):
            return NotImplemented
        return self.seconds >= other.seconds

    def __eq__(self, other: object) -> bool:
        """Compare durations by seconds."""
        if not isinstance(other, TimeDuration):
            return NotImplemented
        return self.seconds == other.seconds

    def __hash__(self) -> int:
        """Hash based on seconds."""
        return hash(self.seconds)
