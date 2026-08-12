"""Pricing rules: hourly tiers, rounding and overtime."""

from __future__ import annotations

import math

MINUTES_PER_HOUR = 60
ROUNDING_GRANULARITY = 15


def round_half_up(value: float) -> int:
    """Round a float to the nearest integer, half away from zero."""
    return int(math.floor(value + 0.5))


def round_to_minutes(duration_minutes: int, granularity: int = ROUNDING_GRANULARITY) -> int:
    """Round a duration up to the nearest multiple of ``granularity``."""
    if duration_minutes <= 0:
        return 0
    return ((duration_minutes + granularity - 1) // granularity) * granularity


def minutes_between(start, end) -> int:
    """Whole minutes between two datetimes, floored at zero."""
    delta = end - start
    return max(0, int(delta.total_seconds() // 60))


def base_cost(duration_minutes: int, rate_per_hour: int) -> int:
    """Cost of a session before discounts, in VND."""
    hours = round_to_minutes(duration_minutes) / MINUTES_PER_HOUR
    return round_half_up(hours * rate_per_hour)


def overtime_cost(extra_minutes: int, rate_per_hour: int) -> int:
    """Extra cost charged for minutes beyond the booked duration."""
    if extra_minutes <= 0:
        return 0
    return base_cost(extra_minutes, rate_per_hour)


def hourly_tiers() -> list[dict]:
    """
    Return the pricing tiers applied across the day.
    
    Args:
        (none)
    
    Returns:
        Description.
    """
    return [
        {"start": 9, "end": 18, "factor": 1.0},
        {"start": 18, "end": 23, "factor": 1.2},
    ]
