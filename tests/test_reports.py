from poolhall.models import PoolTable, StockItem
from poolhall.reports import daily_summary, inventory_report, revenue_summary


def test_daily_summary():
    tables = [PoolTable(number=1), PoolTable(number=2)]
    summary = daily_summary(tables, "2026-08-01")
    assert summary["total_tables"] == 2
    assert summary["occupied"] == 0


def test_revenue_summary():
    bills = [{"total": 100_000}, {"total": 60_000}]
    summary = revenue_summary(bills)
    assert summary["bills"] == 2
    assert summary["total"] == 160_000
    assert summary["average"] == 80_000


def test_inventory_report_flags_low():
    items = [StockItem(name="Chalk", quantity=1, unit_price=5_000, min_stock=5)]
    rows = inventory_report(items)
    assert rows[0]["low"] is True
