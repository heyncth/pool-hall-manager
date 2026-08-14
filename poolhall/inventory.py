"""Stock tracking for drinks and snacks sold at the hall."""

from __future__ import annotations

from .config import LOW_STOCK_THRESHOLD
from .models import StockItem


def create_items() -> list[StockItem]:
    """Return the default stock catalogue."""
    return [
        StockItem(name="Beer (330ml)", quantity=48, unit_price=30_000, min_stock=12),
        StockItem(name="Soda (330ml)", quantity=60, unit_price=15_000, min_stock=12),
        StockItem(name="Snack pack", quantity=30, unit_price=20_000, min_stock=10),
        StockItem(name="Chalk", quantity=24, unit_price=5_000, min_stock=6),
    ]


def find_item(items: list[StockItem], name: str) -> StockItem:
    """Return the stock item with the given name."""
    for item in items:
        if item.name == name:
            return item
    raise KeyError(f"no item named {name!r}")


def restock(items: list[StockItem], name: str, amount: int) -> StockItem:
    """Add stock to an existing item."""
    item = find_item(items, name)
    item.restock(amount)
    return item


def consume(items: list[StockItem], name: str, amount: int) -> StockItem:
    """Remove stock after a sale."""
    item = find_item(items, name)
    item.consume(amount)
    return item


def low_stock(items: list[StockItem], threshold: int = LOW_STOCK_THRESHOLD) -> list[StockItem]:
    """Return items at or below the low-stock threshold."""
    return [item for item in items if item.quantity <= threshold]

def validate_quantity(value: int) -> int:
    """Return ``value`` when non-negative, otherwise raise ValueError."""
    if value < 0:
        raise ValueError("quantity cannot be negative")
    return value
