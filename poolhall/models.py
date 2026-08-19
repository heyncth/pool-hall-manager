"""Core domain models for the pool hall."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging


class TableStatus(Enum):
    """Lifecycle state of a table."""

    FREE = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    OUT_OF_SERVICE = "out_of_service"


class PaymentMethod(Enum):
    """Accepted payment methods."""

    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"


@dataclass
class PoolTable:
    """A billiard table at the hall."""

    number: int
    kind: str = "pool"
    rate_per_hour: int = 0
    status: TableStatus = TableStatus.FREE
    opened_at: datetime | None = None
    reservation: str | None = None

    def is_available(self) -> bool:
        """Return True when the table can be opened right now."""
        return self.status is TableStatus.FREE

    def open(self, when: datetime | None = None) -> None:
        """Open a free table; raise when it is not free."""
        if self.status is not TableStatus.FREE:
            raise ValueError(f"table {self.number} is not free")
        self.status = TableStatus.OCCUPIED
        self.opened_at = when or datetime.now()

    def close(self) -> None:
        """Release an occupied table."""
        if self.status is not TableStatus.OCCUPIED:
            raise ValueError(f"table {self.number} is not occupied")
        self.status = TableStatus.FREE
        self.opened_at = None
        self.reservation = None

    def to_dict(self) -> dict:
        """Serialize the table for JSON storage."""
        return {
            "number": self.number,
            "kind": self.kind,
            "rate_per_hour": self.rate_per_hour,
            "status": self.status.value,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "reservation": self.reservation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PoolTable":
        """Rebuild a table from a JSON dict."""
        opened = datetime.fromisoformat(data["opened_at"]) if data.get("opened_at") else None
        return cls(
            number=data["number"],
            kind=data.get("kind", "pool"),
            rate_per_hour=data.get("rate_per_hour", 0),
            status=TableStatus(data.get("status", TableStatus.FREE.value)),
            opened_at=opened,
            reservation=data.get("reservation"),
        )


@dataclass
class Reservation:
    """A booking for a table at a given time."""

    table_number: int
    customer: str
    start_time: datetime
    duration_minutes: int = 60
    note: str = ""

    def ends_at(self) -> datetime:
        """Return the moment the reservation ends."""
        return self.start_time + timedelta(minutes=self.duration_minutes)

    def to_dict(self) -> dict:
        """Serialize the reservation for JSON storage."""
        return {
            "table_number": self.table_number,
            "customer": self.customer,
            "start_time": self.start_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reservation":
        """Rebuild a reservation from a JSON dict."""
        return cls(
            table_number=data["table_number"],
            customer=data["customer"],
            start_time=datetime.fromisoformat(data["start_time"]),
            duration_minutes=data.get("duration_minutes", 60),
            note=data.get("note", ""),
        )


@dataclass
class StockItem:
    """A consumable sold at the hall (drinks, snacks)."""

    name: str
    quantity: int = 0
    unit_price: int = 0
    min_stock: int = 5

    def is_low(self) -> bool:
        """Return True when stock is at or below the minimum."""
        return self.quantity <= self.min_stock

    def restock(self, amount: int) -> None:
        """Add stock to the item."""
        if amount < 0:
            raise ValueError("restock amount cannot be negative")
        self.quantity += amount

    def consume(self, amount: int) -> None:
        """Remove stock after a sale."""
        if amount < 0:
            raise ValueError("consume amount cannot be negative")
        if amount > self.quantity:
            raise ValueError(f"not enough stock for {self.name}")
        self.quantity -= amount

    def to_dict(self) -> dict:
        """Serialize the item for JSON storage."""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "min_stock": self.min_stock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StockItem":
        """Rebuild an item from a JSON dict."""
        return cls(
            name=data["name"],
            quantity=data.get("quantity", 0),
            unit_price=data.get("unit_price", 0),
            min_stock=data.get("min_stock", 5),
        )

logger = logging.getLogger(__name__)
