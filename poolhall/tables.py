"""Table registry: opening, closing and reservations."""

from __future__ import annotations

from datetime import datetime

from .config import DEFAULT_RATE_PER_HOUR, POOL_TABLE_TYPES
from .models import PoolTable, Reservation, TableStatus


def build_tables(count: int, rate_per_hour: int = DEFAULT_RATE_PER_HOUR) -> list[PoolTable]:
    """Create ``count`` tables with alternating kinds."""
    tables = []
    for number in range(1, count + 1):
        kind = POOL_TABLE_TYPES[(number - 1) % len(POOL_TABLE_TYPES)]
        tables.append(PoolTable(number=number, kind=kind, rate_per_hour=rate_per_hour))
    return tables


def find_table(tables: list[PoolTable], number: int) -> PoolTable:
    """Return the table with the given number."""
    for table in tables:
        if table.number == number:
            return table
    raise KeyError(f"no table #{number}")


def available_tables(tables: list[PoolTable]) -> list[PoolTable]:
    """Return all tables that are currently free."""
    return [t for t in tables if t.is_available()]


def occupied_tables(tables: list[PoolTable]) -> list[PoolTable]:
    """Return all tables currently in use."""
    return [t for t in tables if t.status is TableStatus.OCCUPIED]


def open_table(tables: list[PoolTable], number: int, when: datetime | None = None) -> PoolTable:
    """Open a free table for play."""
    table = find_table(tables, number)
    table.open(when)
    return table


def close_table(tables: list[PoolTable], number: int) -> PoolTable:
    """
    Close an occupied table.
    
    Args:
        tables: Description.
        number: Description.
    
    Returns:
        Description.
    """
    table = find_table(tables, number)
    table.close()
    return table


def has_conflict(reservations: list[Reservation], candidate: Reservation) -> bool:
    """Return True when ``candidate`` overlaps an existing reservation."""
    for existing in reservations:
        if existing.table_number != candidate.table_number:
            continue
        if candidate.start_time < existing.ends_at() and existing.start_time < candidate.ends_at():
            return True
    return False


def add_reservation(reservations: list[Reservation], candidate: Reservation) -> Reservation:
    """Register a reservation, rejecting time conflicts."""
    if has_conflict(reservations, candidate):
        raise ValueError("reservation conflicts with an existing booking")
    reservations.append(candidate)
    return candidate

def _next_free_number(tables: list) -> int:
    """Return the smallest table number that is currently free."""
    for table in sorted(tables, key=lambda t: t.number):
        if table.is_available():
            return table.number
    raise ValueError("no free tables")
