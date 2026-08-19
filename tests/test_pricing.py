from datetime import datetime
from poolhall.pricing import base_cost, minutes_between, overtime_cost, round_half_up, round_to_minutes


def test_round_half_up():
    assert round_half_up(1.4) == 1
    assert round_half_up(1.5) == 2


def test_round_to_minutes():
    assert round_to_minutes(10) == 15
    assert round_to_minutes(15) == 15
    assert round_to_minutes(0) == 0


def test_minutes_between():
    start = datetime(2026, 8, 1, 10, 0)
    end = datetime(2026, 8, 1, 10, 45)
    assert minutes_between(start, end) == 45


def test_base_cost():
    assert base_cost(60, 60_000) == 60_000
    assert base_cost(15, 60_000) == 15_000


def test_overtime_cost_free_for_early_close():
    assert overtime_cost(0, 60_000) == 0

def test_overtime_cost_charges():
    assert overtime_cost(30, 60_000) == 30_000

def test_base_cost_rounds_up():
    assert base_cost(10, 60_000) == 15_000
