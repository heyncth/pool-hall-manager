"""Simple in-app notifications for low stock and reservations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Notification:
    """A single message shown to the operator."""

    message: str
    created_at: datetime = field(default_factory=datetime.now)
    read: bool = False

    def mark_read(self) -> None:
        """Mark the notification as read."""
        self.read = True


def low_stock_notices(items) -> list[str]:
    """Build a notice for every item below its minimum stock."""
    return [f"{item.name} is low ({item.quantity} left)" for item in items if item.is_low()]


def reservation_notice(reservation) -> str:
    """Build a notice for an upcoming reservation."""
    return (
        f"table #{reservation.table_number} reserved for {reservation.customer} "
        f"at {reservation.start_time:%H:%M}"
    )
