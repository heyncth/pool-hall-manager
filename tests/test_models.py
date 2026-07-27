import pytest
from datetime import datetime

from poolhall.models import PoolTable, Reservation, StockItem, TableStatus


def test_table_open_and_close():
    table = PoolTable(number=1)
    assert table.is_available()
    table.open()
    assert table.status is TableStatus.OCCUPIED
    table.close()
    assert table.is_available()


def test_table_cannot_close_free_table():
    with pytest.raises(ValueError):
        PoolTable(number=2).close()


def test_stock_consume_guard():
    item = StockItem(name="Chalk", quantity=2)
    with pytest.raises(ValueError):
        item.consume(5)


def test_stock_low_flag():
    assert StockItem(name="Chalk", quantity=4, min_stock=5).is_low()


def test_reservation_ends_at():
    res = Reservation(
        table_number=1,
        customer="An",
        start_time=datetime(2026, 8, 1, 12, 0),
        duration_minutes=90,
    )
    assert res.ends_at() == datetime(2026, 8, 1, 13, 30)


def test_table_roundtrip():
    table = PoolTable(number=4, kind="snooker", rate_per_hour=80_000)
    assert PoolTable.from_dict(table.to_dict()) == table
