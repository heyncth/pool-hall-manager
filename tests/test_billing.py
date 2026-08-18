from datetime import datetime

import pytest

from poolhall.billing import apply_discount, calculate_bill
from poolhall.models import PaymentMethod


def test_apply_discount():
    assert apply_discount(100_000, 10) == 10_000


def test_apply_discount_rejects_out_of_range():
    with pytest.raises(ValueError):
        apply_discount(100_000, 150)


def test_calculate_bill_total():
    start = datetime(2026, 8, 1, 10, 0)
    end = datetime(2026, 8, 1, 11, 0)
    bill = calculate_bill(3, start, end, 60_000, payment_method=PaymentMethod.CASH)
    assert bill.duration_minutes == 60
    assert bill.subtotal == 60_000
    assert bill.total > bill.subtotal


def test_calculate_bill_with_discount():
    start = datetime(2026, 8, 1, 10, 0)
    end = datetime(2026, 8, 1, 11, 0)
    bill = calculate_bill(3, start, end, 60_000, discount_percent=10.0)
    assert bill.discount == 6_000

def test_bill_to_dict_roundtrip():
    start = datetime(2026, 8, 1, 10, 0)
    end = datetime(2026, 8, 1, 11, 0)
    bill = calculate_bill(2, start, end, 60_000)
    assert bill.to_dict()["table_number"] == 2
