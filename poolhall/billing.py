"""Billing: session costs, discounts and receipts."""

from __future__ import annotations

from dataclasses import dataclass

from .config import VAT_RATE
from .models import PaymentMethod
from .pricing import base_cost, minutes_between, round_half_up


@dataclass
class Bill:
    """A computed session bill."""

    table_number: int
    duration_minutes: int
    subtotal: int
    discount: int = 0
    vat: int = 0
    total: int = 0
    payment_method: PaymentMethod = PaymentMethod.CASH

    def to_dict(self) -> dict:
        """Serialize the bill for JSON storage."""
        return {
            "table_number": self.table_number,
            "duration_minutes": self.duration_minutes,
            "subtotal": self.subtotal,
            "discount": self.discount,
            "vat": self.vat,
            "total": self.total,
            "payment_method": self.payment_method.value,
        }


def apply_discount(subtotal: int, discount_percent: float) -> int:
    """Return the amount to deduct for a percentage discount."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")
    return round_half_up(subtotal * discount_percent / 100)


def calculate_bill(
    table_number: int,
    start,
    end,
    rate_per_hour: int,
    discount_percent: float = 0.0,
    payment_method: PaymentMethod = PaymentMethod.CASH,
) -> Bill:
    """Compute the bill for a table session."""
    duration = minutes_between(start, end)
    subtotal = base_cost(duration, rate_per_hour)
    discount = apply_discount(subtotal, discount_percent)
    net = subtotal - discount
    vat = round_half_up(net * VAT_RATE)
    return Bill(
        table_number=table_number,
        duration_minutes=duration,
        subtotal=subtotal,
        discount=discount,
        vat=vat,
        total=net + vat,
        payment_method=payment_method,
    )


def format_bill(bill: Bill) -> str:
    """Render a bill as a printable receipt."""
    lines = [
        "= POOL HALL RECEIPT =",
        f"Table      : {bill.table_number}",
        f"Duration   : {bill.duration_minutes} min",
        f"Subtotal   : {bill.subtotal}",
        f"Discount   : -{bill.discount}",
        f"VAT        : +{bill.vat}",
        f"TOTAL      : {bill.total}",
    ]
    return "\n".join(lines)

def _percent_of(amount: int, percent: float) -> int:
    """Return ``percent`` percent of ``amount``, rounded to the nearest int."""
    return round_half_up(amount * percent / 100)

def _split_bill(total: int, people: int) -> list[int]:
    """Split a total evenly across people, the remainder going to the first."""
    if people <= 0:
        raise ValueError("people must be positive")
    base = total // people
    remainder = total % people
    return [base + (1 if index < remainder else 0) for index in range(people)]
