"""Daily reports: sessions, revenue and inventory status."""

from __future__ import annotations

from datetime import date

from .models import PoolTable, StockItem


def daily_summary(tables: list[PoolTable], date_iso: str) -> dict:
    """Summarize the day: total tables and current occupancy."""
    occupied = [t for t in tables if t.status.value == "occupied"]
    return {
        "date": date_iso,
        "total_tables": len(tables),
        "occupied": len(occupied),
        "free": len(tables) - len(occupied),
    }


def revenue_summary(bills: list[dict]) -> dict:
    """
    Aggregate revenue from a list of bill dicts.
    
    Args:
        bills: Description.
    
    Returns:
        Description.
    """
    total = sum(b.get("total", 0) for b in bills)
    count = len(bills)
    average = round(total / count) if count else 0
    return {"bills": count, "total": total, "average": average}


def inventory_report(items: list[StockItem]) -> list[dict]:
    """Build a printable inventory status report."""
    return [
        {
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "low": item.is_low(),
        }
        for item in items
    ]


def today_iso() -> str:
    """Return today's date as an ISO string."""
    return date.today().isoformat()

def _percent(part: int, whole: int) -> float:
    """Percentage of ``part`` over ``whole``, or 0.0 when whole is zero."""
    if whole <= 0:
        return 0.0
    return round(part * 100 / whole, 1)
