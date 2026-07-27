from datetime import datetime

import pytest

from poolhall.models import Reservation
from poolhall.tables import (
    add_reservation,
    available_tables,
    build_tables,
    close_table,
    find_table,
    has_conflict,
    occupied_tables,
    open_table,
)


def test_build_tables_kinds():
    tables = build_tables(3)
    assert len(tables) == 3
    assert tables[0].kind == "pool"


def test_find_table():
    tables = build_tables(5)
    assert find_table(tables, 3).number == 3
    with pytest.raises(KeyError):
        find_table(tables, 99)


def test_open_close():
    tables = build_tables(2)
    open_table(tables, 1)
    assert not tables[0].is_available()
    close_table(tables, 1)
    assert tables[0].is_available()


def test_conflict_detection():
    r1 = Reservation(table_number=1, customer="A", start_time=datetime(2026, 8, 1, 12, 0), duration_minutes=60)
    r2 = Reservation(table_number=1, customer="B", start_time=datetime(2026, 8, 1, 12, 30), duration_minutes=60)
    assert has_conflict([r1], r2)


def test_add_reservation_rejects_conflict():
    r1 = Reservation(table_number=1, customer="A", start_time=datetime(2026, 8, 1, 12, 0), duration_minutes=60)
    r2 = Reservation(table_number=1, customer="B", start_time=datetime(2026, 8, 1, 12, 30), duration_minutes=60)
    with pytest.raises(ValueError):
        add_reservation([r1], r2)
