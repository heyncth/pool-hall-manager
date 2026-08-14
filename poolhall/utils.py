"""Small shared helpers used across the project."""

from __future__ import annotations

import re
from datetime import datetime, time


def clamp(value: int, low: int, high: int) -> int:
    """Constrain ``value`` between ``low`` and ``high``."""
    return max(low, min(high, value))


def format_currency(amount: int) -> str:
    """Format an integer amount with thousand separators and a suffix."""
    return f"{amount:,} VND"


def parse_time(value: str) -> time:
    """Parse a 24h ``HH:MM`` string into a ``time`` object."""
    hour, minute = value.split(":")
    return time(hour=int(hour), minute=int(minute))


def parse_datetime(value: str, fmt: str = "%Y-%m-%d %H:%M") -> datetime:
    """Parse a datetime string; raises ValueError on bad input."""
    return datetime.strptime(value, fmt)


def slugify(value: str) -> str:
    """Turn arbitrary text into a URL-safe slug."""
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def is_within_hours(when: datetime, opening: int, closing: int) -> bool:
    """Return True when ``when`` falls inside opening hours."""
    return opening <= when.hour < closing
