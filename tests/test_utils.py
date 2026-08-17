from datetime import datetime
from poolhall.utils import clamp, format_currency, is_within_hours, parse_time, slugify


def test_clamp_bounds():
    assert clamp(5, 0, 10) == 5
    assert clamp(-3, 0, 10) == 0
    assert clamp(42, 0, 10) == 10


def test_format_currency():
    assert format_currency(60_000) == "60,000 VND"


def test_slugify():
    assert slugify("Pool Hall 2026!") == "pool-hall-2026"


def test_parse_time():
    parsed = parse_time("09:30")
    assert (parsed.hour, parsed.minute) == (9, 30)


def test_is_within_hours():
    assert is_within_hours(datetime(2026, 8, 1, 12), 9, 23)
    assert not is_within_hours(datetime(2026, 8, 1, 23, 30), 9, 23)

def test_clamp_identity():
    assert clamp(7, 0, 10) == 7

def test_slugify_multiple_spaces():
    assert slugify("  Hello   World  ") == "hello-world"
