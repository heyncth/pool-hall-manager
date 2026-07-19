"""Application settings and shared constants."""

from __future__ import annotations

from pathlib import Path

DATA_DIR = Path.home() / ".poolhall"
DATA_FILE = DATA_DIR / "poolhall.json"

OPENING_HOUR = 9
CLOSING_HOUR = 23
DEFAULT_RATE_PER_HOUR = 60_000
VAT_RATE = 0.08
MINUTES_PER_HOUR = 60

TABLE_COUNT = 12
POOL_TABLE_TYPES = ("pool", "snooker", "carom")

MAX_RESERVATIONS_PER_TABLE = 4
LOW_STOCK_THRESHOLD = 5
