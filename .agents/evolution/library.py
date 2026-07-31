"""Static content for the Repository Evolution Engine.

Two kinds of data live here:

* ``PACKAGE`` — the hand-written pool hall CLI project (fixtures) used by
  ``bootstrap.py`` to create the "ported from Java" commit history.
* ``POOLS`` — small vocabulary pools used by ``mutation.py`` when applying
  boundary-safe changes (new helpers, constants, validators, tests, README
  sections and brand-new modules).

No code in this module is ever generated at runtime; everything is static
fixture content written once.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
#  PACKAGE — the ported pool hall CLI project (bootstrap fixtures)
# ═══════════════════════════════════════════════════════════════════════════════

PYPROJECT = """\
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "poolhall-cli"
version = "0.1.0"
description = "Command-line manager for pool hall tables, billing and stock."
requires-python = ">=3.10"

[project.scripts]
poolhall = "poolhall.cli:main"

[tool.setuptools.packages.find]
include = ["poolhall*"]
"""

README = """\
# Pool Hall Manager

A command-line tool to run a billiards hall: track table occupancy, compute
session bills, keep reservations and manage the stock of drinks and snacks.

This project started as a Java Swing prototype for a final course project and
was later ported to a Python CLI so it can be driven from the terminal and
scripted easily.

## Install

```bash
pip install -e .
```

## Usage

```bash
# open table 3 for play
poolhall open 3

# close table 3 and print the receipt
poolhall close 3 --discount 10

# reserve table 5 for a customer at 20:00
poolhall reserve 5 "Nguyen An" 20:00 --minutes 90

# check stock levels
poolhall inventory
poolhall inventory --restock "Chalk" 12

# daily report
poolhall report

# table status overview
poolhall status
```

## Configuration

Data is stored as JSON under `~/.poolhall/`. Defaults such as the hourly
rate, opening hours and VAT live in `poolhall/config.py` and can be tweaked
there without touching the CLI.

## Tests

```bash
python -m pytest tests/
```
"""

INIT = '"""Pool hall management toolkit."""\n\n__version__ = "0.1.0"\n'

CONFIG = '''\
"""Application settings and shared constants."""

from __future__ import annotations

from pathlib import Path

DATA_DIR = Path.home() / ".poolhall"
DATA_FILE = DATA_DIR / "poolhall.json"

OPENING_HOUR = 9
CLOSING_HOUR = 23
DEFAULT_RATE_PER_HOUR = 60_000
VAT_RATE = 0.08
MINUTES_PER_HOUR = 60

TABLE_COUNT = 12
POOL_TABLE_TYPES = ("pool", "snooker", "carom")

MAX_RESERVATIONS_PER_TABLE = 4
LOW_STOCK_THRESHOLD = 5
'''

MODELS = '''\
"""Core domain models for the pool hall."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


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
'''

PRICING = '''\
"""Pricing rules: hourly tiers, rounding and overtime."""

from __future__ import annotations

import math

MINUTES_PER_HOUR = 60
ROUNDING_GRANULARITY = 15


def round_half_up(value: float) -> int:
    """Round a float to the nearest integer, half away from zero."""
    return int(math.floor(value + 0.5))


def round_to_minutes(duration_minutes: int, granularity: int = ROUNDING_GRANULARITY) -> int:
    """Round a duration up to the nearest multiple of ``granularity``."""
    if duration_minutes <= 0:
        return 0
    return ((duration_minutes + granularity - 1) // granularity) * granularity


def minutes_between(start, end) -> int:
    """Whole minutes between two datetimes, floored at zero."""
    delta = end - start
    return max(0, int(delta.total_seconds() // 60))


def base_cost(duration_minutes: int, rate_per_hour: int) -> int:
    """Cost of a session before discounts, in VND."""
    hours = round_to_minutes(duration_minutes) / MINUTES_PER_HOUR
    return round_half_up(hours * rate_per_hour)


def overtime_cost(extra_minutes: int, rate_per_hour: int) -> int:
    """Extra cost charged for minutes beyond the booked duration."""
    if extra_minutes <= 0:
        return 0
    return base_cost(extra_minutes, rate_per_hour)


def hourly_tiers() -> list[dict]:
    """Return the pricing tiers applied across the day."""
    return [
        {"start": 9, "end": 18, "factor": 1.0},
        {"start": 18, "end": 23, "factor": 1.2},
    ]
'''

STORAGE = '''\
"""JSON persistence for the pool hall state."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def _atomic_write(path: Path, content: str) -> None:
    """Write content to ``path`` atomically through a temp file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def save_json(path: Path, data: Any) -> None:
    """Serialize ``data`` to a JSON file safely."""
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))


def load_json(path: Path, default: Any = None) -> Any:
    """Load a JSON file; return ``default`` when missing or broken."""
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return default


def read_text(path: Path) -> str | None:
    """Return file text, or None when the file is missing."""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """Write text content to a file atomically."""
    _atomic_write(path, content)
'''

TABLES = '''\
"""Table registry: opening, closing and reservations."""

from __future__ import annotations

from datetime import datetime

from .config import DEFAULT_RATE_PER_HOUR, POOL_TABLE_TYPES
from .models import PoolTable, Reservation, TableStatus


def build_tables(count: int, rate_per_hour: int = DEFAULT_RATE_PER_HOUR) -> list[PoolTable]:
    """Create ``count`` tables with alternating kinds."""
    tables = []
    for number in range(1, count + 1):
        kind = POOL_TABLE_TYPES[(number - 1) % len(POOL_TABLE_TYPES)]
        tables.append(PoolTable(number=number, kind=kind, rate_per_hour=rate_per_hour))
    return tables


def find_table(tables: list[PoolTable], number: int) -> PoolTable:
    """Return the table with the given number."""
    for table in tables:
        if table.number == number:
            return table
    raise KeyError(f"no table #{number}")


def available_tables(tables: list[PoolTable]) -> list[PoolTable]:
    """Return all tables that are currently free."""
    return [t for t in tables if t.is_available()]


def occupied_tables(tables: list[PoolTable]) -> list[PoolTable]:
    """Return all tables currently in use."""
    return [t for t in tables if t.status is TableStatus.OCCUPIED]


def open_table(tables: list[PoolTable], number: int, when: datetime | None = None) -> PoolTable:
    """Open a free table for play."""
    table = find_table(tables, number)
    table.open(when)
    return table


def close_table(tables: list[PoolTable], number: int) -> PoolTable:
    """Close an occupied table."""
    table = find_table(tables, number)
    table.close()
    return table


def has_conflict(reservations: list[Reservation], candidate: Reservation) -> bool:
    """Return True when ``candidate`` overlaps an existing reservation."""
    for existing in reservations:
        if existing.table_number != candidate.table_number:
            continue
        if candidate.start_time < existing.ends_at() and existing.start_time < candidate.ends_at():
            return True
    return False


def add_reservation(reservations: list[Reservation], candidate: Reservation) -> Reservation:
    """Register a reservation, rejecting time conflicts."""
    if has_conflict(reservations, candidate):
        raise ValueError("reservation conflicts with an existing booking")
    reservations.append(candidate)
    return candidate
'''

INVENTORY = '''\
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
'''

REPORTS = '''\
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
    """Aggregate revenue from a list of bill dicts."""
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
'''

UTILS = '''\
"""Small shared helpers used across the project."""

from __future__ import annotations

import re
from datetime import datetime, time


def clamp(value: int, low: int, high: int) -> int:
    """Constrain ``value`` between ``low`` and ``high``."""
    return max(low, min(high, value))


def format_currency(amount: int) -> str:
    """Format an integer amount with thousand separators and a suffix."""
    return f"{amount:,} VND"


def parse_time(value: str) -> time:
    """Parse a 24h ``HH:MM`` string into a ``time`` object."""
    hour, minute = value.split(":")
    return time(hour=int(hour), minute=int(minute))


def parse_datetime(value: str, fmt: str = "%Y-%m-%d %H:%M") -> datetime:
    """Parse a datetime string; raises ValueError on bad input."""
    return datetime.strptime(value, fmt)


def slugify(value: str) -> str:
    """Turn arbitrary text into a URL-safe slug."""
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def is_within_hours(when: datetime, opening: int, closing: int) -> bool:
    """Return True when ``when`` falls inside opening hours."""
    return opening <= when.hour < closing
'''

BILLING = '''\
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
    return "\\n".join(lines)
'''

CLI = '''\
"""Command-line interface for the pool hall manager."""

from __future__ import annotations

import argparse
from datetime import datetime

from . import __version__
from .billing import calculate_bill, format_bill
from .config import DATA_FILE, TABLE_COUNT
from .inventory import consume, create_items, restock
from .models import PaymentMethod, PoolTable, Reservation, StockItem
from .reports import daily_summary, inventory_report, revenue_summary
from .storage import load_json, save_json
from .tables import add_reservation, build_tables, close_table, find_table, open_table
from .utils import format_currency, parse_time


def _load() -> dict:
    """Load persisted state, or an empty dict on first run."""
    return load_json(DATA_FILE, default={})


def _save(state: dict) -> None:
    """Persist the state dict."""
    save_json(DATA_FILE, state)


def _bootstrap(state: dict) -> None:
    """Seed defaults on the very first run."""
    if not state.get("tables"):
        state["tables"] = [t.to_dict() for t in build_tables(TABLE_COUNT)]
    if not state.get("items"):
        state["items"] = [i.to_dict() for i in create_items()]


def _tables(state: dict) -> list[PoolTable]:
    return [PoolTable.from_dict(t) for t in state.get("tables", [])]


def _items(state: dict) -> list[StockItem]:
    return [StockItem.from_dict(i) for i in state.get("items", [])]


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(prog="poolhall", description="Manage pool hall tables, billing and stock.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("open", help="open a free table")
    p.add_argument("table", type=int)

    p = sub.add_parser("close", help="close a table and print its bill")
    p.add_argument("table", type=int)
    p.add_argument("--discount", type=float, default=0.0, help="discount percentage")
    p.add_argument("--method", choices=[m.value for m in PaymentMethod], default="cash")

    p = sub.add_parser("reserve", help="reserve a table")
    p.add_argument("table", type=int)
    p.add_argument("customer")
    p.add_argument("start", help="start time, HH:MM")
    p.add_argument("--minutes", type=int, default=60)

    p = sub.add_parser("inventory", help="show or update stock")
    p.add_argument("--restock", nargs=2, metavar=("NAME", "AMOUNT"))
    p.add_argument("--consume", nargs=2, metavar=("NAME", "AMOUNT"))

    p = sub.add_parser("report", help="print the daily report")
    p.add_argument("--date", default=None)

    sub.add_parser("status", help="list tables and their state")
    return parser


def _cmd_open(args, tables, items, state) -> int:
    table = open_table(tables, args.table)
    print(f"opened table #{table.number} ({table.kind})")
    return 0


def _cmd_close(args, tables, items, state) -> int:
    table = find_table(tables, args.table)
    if table.opened_at is None:
        print(f"table #{args.table} is not open")
        return 1
    bill = calculate_bill(
        args.table,
        table.opened_at,
        datetime.now(),
        table.rate_per_hour,
        args.discount,
        PaymentMethod(args.method),
    )
    close_table(tables, args.table)
    state.setdefault("bills", []).append(bill.to_dict())
    print(format_bill(bill))
    return 0


def _cmd_reserve(args, tables, items, state) -> int:
    start = datetime.combine(datetime.now().date(), parse_time(args.start))
    reservations = [Reservation.from_dict(r) for r in state.get("reservations", [])]
    candidate = Reservation(
        table_number=args.table,
        customer=args.customer,
        start_time=start,
        duration_minutes=args.minutes,
    )
    try:
        add_reservation(reservations, candidate)
    except ValueError as exc:
        print(f"error: {exc}")
        return 1
    state["reservations"] = [r.to_dict() for r in reservations]
    print(f"reserved table #{args.table} for {args.customer}")
    return 0


def _cmd_inventory(args, tables, items, state) -> int:
    try:
        if args.restock:
            name, amount = args.restock
            item = restock(items, name, int(amount))
            print(f"{item.name}: {item.quantity}")
        elif args.consume:
            name, amount = args.consume
            item = consume(items, name, int(amount))
            print(f"{item.name}: {item.quantity}")
        else:
            for row in inventory_report(items):
                flag = " (low)" if row["low"] else ""
                print(f"{row['name']:<20} {row['quantity']:>4}{flag} {format_currency(row['unit_price'])}")
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}")
        return 1
    state["items"] = [i.to_dict() for i in items]
    return 0


def _cmd_report(args, tables, items, state) -> int:
    summary = daily_summary(tables, args.date or datetime.now().date().isoformat())
    print(f"date={summary['date']} tables={summary['total_tables']} occupied={summary['occupied']} free={summary['free']}")
    revenue = revenue_summary(state.get("bills", []))
    print(f"bills={revenue['bills']} total={format_currency(revenue['total'])} avg={format_currency(revenue['average'])}")
    return 0


def _cmd_status(args, tables, items, state) -> int:
    for table in tables:
        print(f"#{table.number:<3} {table.kind:<8} {table.status.value}")
    return 0


_HANDLERS = {
    "open": _cmd_open,
    "close": _cmd_close,
    "reserve": _cmd_reserve,
    "inventory": _cmd_inventory,
    "report": _cmd_report,
    "status": _cmd_status,
}


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``poolhall`` console script."""
    args = build_parser().parse_args(argv)
    if not args.command:
        build_parser().print_help()
        return 0
    state = _load()
    _bootstrap(state)
    tables = _tables(state)
    items = _items(state)
    code = _HANDLERS[args.command](args, tables, items, state)
    state["tables"] = [t.to_dict() for t in tables]
    _save(state)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
'''

TESTS = {
    "tests/test_models.py": '''\
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
''',
    "tests/test_pricing.py": '''\
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
''',
    "tests/test_billing.py": '''\
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
''',
    "tests/test_tables.py": '''\
from datetime import datetime

import pytest

from poolhall.models import Reservation
from poolhall.tables import (
    add_reservation,
    available_tables,
    build_tables,
    close_table,
    find_table,
    has_conflict,
    occupied_tables,
    open_table,
)


def test_build_tables_kinds():
    tables = build_tables(3)
    assert len(tables) == 3
    assert tables[0].kind == "pool"


def test_find_table():
    tables = build_tables(5)
    assert find_table(tables, 3).number == 3
    with pytest.raises(KeyError):
        find_table(tables, 99)


def test_open_close():
    tables = build_tables(2)
    open_table(tables, 1)
    assert not tables[0].is_available()
    close_table(tables, 1)
    assert tables[0].is_available()


def test_conflict_detection():
    r1 = Reservation(table_number=1, customer="A", start_time=datetime(2026, 8, 1, 12, 0), duration_minutes=60)
    r2 = Reservation(table_number=1, customer="B", start_time=datetime(2026, 8, 1, 12, 30), duration_minutes=60)
    assert has_conflict([r1], r2)


def test_add_reservation_rejects_conflict():
    r1 = Reservation(table_number=1, customer="A", start_time=datetime(2026, 8, 1, 12, 0), duration_minutes=60)
    r2 = Reservation(table_number=1, customer="B", start_time=datetime(2026, 8, 1, 12, 30), duration_minutes=60)
    with pytest.raises(ValueError):
        add_reservation([r1], r2)
''',
    "tests/test_inventory.py": '''\
import pytest

from poolhall.inventory import consume, create_items, low_stock, restock


def test_create_items_defaults():
    items = create_items()
    assert len(items) >= 4


def test_restock():
    items = create_items()
    item = restock(items, "Chalk", 10)
    assert item.quantity > 0


def test_consume():
    items = create_items()
    item = consume(items, "Chalk", 1)
    assert item.quantity == 23


def test_consume_missing_item():
    with pytest.raises(KeyError):
        consume(create_items(), "Nope", 1)


def test_low_stock():
    items = create_items()
    items[0].quantity = 1
    assert items[0] in low_stock(items)
''',
    "tests/test_storage.py": '''\
from poolhall.storage import load_json, read_text, save_json, write_text


def test_save_load_roundtrip(tmp_path):
    path = tmp_path / "data.json"
    save_json(path, {"a": [1, 2]})
    assert load_json(path) == {"a": [1, 2]}


def test_load_missing_returns_default(tmp_path):
    assert load_json(tmp_path / "nope.json", default=[]) == []


def test_load_broken_returns_default(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json")
    assert load_json(path, default=None) is None


def test_write_read_text(tmp_path):
    path = tmp_path / "f.txt"
    write_text(path, "hello")
    assert read_text(path) == "hello"
    assert read_text(tmp_path / "missing.txt") is None
''',
    "tests/test_reports.py": '''\
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
''',
    "tests/test_utils.py": '''\
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
''',
}

PACKAGE: dict[str, str] = {
    "pyproject.toml": PYPROJECT,
    "README.md": README,
    "poolhall/__init__.py": INIT,
    "poolhall/config.py": CONFIG,
    "poolhall/models.py": MODELS,
    "poolhall/pricing.py": PRICING,
    "poolhall/storage.py": STORAGE,
    "poolhall/tables.py": TABLES,
    "poolhall/inventory.py": INVENTORY,
    "poolhall/reports.py": REPORTS,
    "poolhall/utils.py": UTILS,
    "poolhall/billing.py": BILLING,
    "poolhall/cli.py": CLI,
    **TESTS,
}

# ═══════════════════════════════════════════════════════════════════════════════
#  POOLS — vocabulary used by the evolution mutations
# ═══════════════════════════════════════════════════════════════════════════════

# New small helper functions, keyed by module, appended at the end of a file.
HELPERS: dict[str, list[tuple[str, str]]] = {
    "billing": [
        (
            "_split_bill",
            '''def _split_bill(total: int, people: int) -> list[int]:
    """Split a total evenly across people, the remainder going to the first."""
    if people <= 0:
        raise ValueError("people must be positive")
    base = total // people
    remainder = total % people
    return [base + (1 if index < remainder else 0) for index in range(people)]
''',
        ),
        (
            "_percent_of",
            '''def _percent_of(amount: int, percent: float) -> int:
    """Return ``percent`` percent of ``amount``, rounded to the nearest int."""
    return round_half_up(amount * percent / 100)
''',
        ),
    ],
    "pricing": [
        (
            "_quantize",
            '''def _quantize(value: int, step: int) -> int:
    """Round ``value`` down to the nearest multiple of ``step``."""
    if step <= 0:
        raise ValueError("step must be positive")
    return (value // step) * step
''',
        ),
        (
            "_peak_adjusted",
            '''def _peak_adjusted(cost: int, hour: int) -> int:
    """Apply the peak-hour factor to a cost, rounded up."""
    tiers = hourly_tiers()
    for tier in tiers:
        if tier["start"] <= hour < tier["end"]:
            return round_half_up(cost * tier["factor"])
    return cost
''',
        ),
    ],
    "tables": [
        (
            "_count_by_status",
            '''def _count_by_status(tables: list, status: TableStatus) -> int:
    """Count tables currently in the given status."""
    return sum(1 for table in tables if table.status is status)
''',
        ),
        (
            "_next_free_number",
            '''def _next_free_number(tables: list) -> int:
    """Return the smallest table number that is currently free."""
    for table in sorted(tables, key=lambda t: t.number):
        if table.is_available():
            return table.number
    raise ValueError("no free tables")
''',
        ),
    ],
    "inventory": [
        (
            "_stock_value",
            '''def _stock_value(items: list) -> int:
    """Total value of all stock at current unit prices."""
    return sum(item.quantity * item.unit_price for item in items)
''',
        ),
        (
            "_sold_value",
            '''def _sold_value(item) -> int:
    """Value of a single unit sold, in VND."""
    return item.unit_price
''',
        ),
    ],
    "storage": [
        (
            "_backup_path",
            '''def _backup_path(path: Path) -> Path:
    """Return the backup path for a file (a sibling with a .bak suffix)."""
    return path.with_suffix(path.suffix + ".bak")
''',
        ),
        (
            "_is_valid_json",
            '''def _is_valid_json(text: str) -> bool:
    """Return True when ``text`` parses as JSON."""
    try:
        json.loads(text)
        return True
    except ValueError:
        return False
''',
        ),
    ],
    "reports": [
        (
            "_percent",
            '''def _percent(part: int, whole: int) -> float:
    """Percentage of ``part`` over ``whole``, or 0.0 when whole is zero."""
    if whole <= 0:
        return 0.0
    return round(part * 100 / whole, 1)
''',
        ),
    ],
    "utils": [
        (
            "_coerce_int",
            '''def _coerce_int(value) -> int:
    """Coerce a value to int, raising ValueError for bad input."""
    if isinstance(value, bool):
        raise ValueError("bool is not an int")
    return int(value)
''',
        ),
        (
            "_ensure_list",
            '''def _ensure_list(value) -> list:
    """Return ``value`` wrapped in a list when it is not already one."""
    if isinstance(value, list):
        return value
    return [value]
''',
        ),
    ],
    "config": [
        (
            "_env_int",
            '''def _env_int(name: str, default: int) -> int:
    """Read an integer from the environment, falling back to ``default``."""
    import os

    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default
''',
        ),
    ],
}

# New module-level constants, keyed by module.
CONSTANTS: dict[str, list[tuple[str, str]]] = {
    "config": [
        ("MAX_RESERVATION_DAYS", "30"),
        ("BOOKING_BUFFER_MINUTES", "15"),
        ("DEPOSIT_AMOUNT", "100_000"),
    ],
    "billing": [
        ("MINIMUM_BILL", "20_000"),
        ("ROUNDING_STEP", "1_000"),
    ],
    "pricing": [
        ("PEAK_FACTOR", "1.2"),
        ("MIN_CHARGE_MINUTES", "30"),
    ],
    "tables": [
        ("MAX_RESERVATION_DURATION", "240"),
    ],
    "inventory": [
        ("SERVICE_CHARGE", "10_000"),
    ],
    "reports": [
        ("TOP_N", "5"),
    ],
}

# Small validation helpers, keyed by module.
VALIDATORS: dict[str, list[tuple[str, str]]] = {
    "billing": [
        (
            "validate_positive_amount",
            '''def validate_positive_amount(value: int, label: str = "amount") -> int:
    """Return ``value`` when positive, otherwise raise ValueError."""
    if value <= 0:
        raise ValueError(f"{label} must be positive")
    return value
''',
        ),
    ],
    "tables": [
        (
            "validate_table_number",
            '''def validate_table_number(number: int, tables: list) -> int:
    """Return ``number`` when it matches an existing table."""
    find_table(tables, number)
    return number
''',
        ),
    ],
    "inventory": [
        (
            "validate_quantity",
            '''def validate_quantity(value: int) -> int:
    """Return ``value`` when non-negative, otherwise raise ValueError."""
    if value < 0:
        raise ValueError("quantity cannot be negative")
    return value
''',
        ),
    ],
    "pricing": [
        (
            "validate_rate",
            '''def validate_rate(rate_per_hour: int) -> int:
    """Return the rate when it is strictly positive."""
    if rate_per_hour <= 0:
        raise ValueError("rate_per_hour must be positive")
    return rate_per_hour
''',
        ),
    ],
}

# Extra test functions, keyed by module. They reuse names already imported by
# the bootstrap test files (see PACKAGE tests).
TESTS_POOL: dict[str, list[tuple[str, str]]] = {
    "billing": [
        (
            "test_calculate_bill_overtime",
            '''def test_calculate_bill_overtime():
    start = datetime(2026, 8, 1, 10, 0)
    end = datetime(2026, 8, 1, 11, 30)
    bill = calculate_bill(1, start, end, 60_000)
    assert bill.duration_minutes == 90
''',
        ),
        (
            "test_bill_to_dict_roundtrip",
            '''def test_bill_to_dict_roundtrip():
    start = datetime(2026, 8, 1, 10, 0)
    end = datetime(2026, 8, 1, 11, 0)
    bill = calculate_bill(2, start, end, 60_000)
    assert bill.to_dict()["table_number"] == 2
''',
        ),
        (
            "test_apply_discount_zero",
            '''def test_apply_discount_zero():
    assert apply_discount(100_000, 0) == 0
''',
        ),
    ],
    "pricing": [
        (
            "test_base_cost_rounds_up",
            '''def test_base_cost_rounds_up():
    assert base_cost(10, 60_000) == 15_000
''',
        ),
        (
            "test_overtime_cost_charges",
            '''def test_overtime_cost_charges():
    assert overtime_cost(30, 60_000) == 30_000
''',
        ),
    ],
    "tables": [
        (
            "test_available_tables_empty",
            '''def test_available_tables_empty():
    tables = build_tables(1)
    open_table(tables, 1)
    assert available_tables(tables) == []
''',
        ),
        (
            "test_occupied_tables_after_open",
            '''def test_occupied_tables_after_open():
    tables = build_tables(2)
    open_table(tables, 1)
    assert len(occupied_tables(tables)) == 1
''',
        ),
    ],
    "inventory": [
        (
            "test_restock_negative_rejected",
            '''def test_restock_negative_rejected():
    with pytest.raises(ValueError):
        restock(create_items(), "Chalk", -1)
''',
        ),
    ],
    "storage": [
        (
            "test_save_overwrites",
            '''def test_save_overwrites(tmp_path):
    path = tmp_path / "data.json"
    save_json(path, {"v": 1})
    save_json(path, {"v": 2})
    assert load_json(path) == {"v": 2}
''',
        ),
    ],
    "utils": [
        (
            "test_clamp_identity",
            '''def test_clamp_identity():
    assert clamp(7, 0, 10) == 7
''',
        ),
        (
            "test_slugify_multiple_spaces",
            '''def test_slugify_multiple_spaces():
    assert slugify("  Hello   World  ") == "hello-world"
''',
        ),
    ],
    "models": [
        (
            "test_table_open_with_time",
            '''def test_table_open_with_time():
    table = PoolTable(number=1)
    table.open(datetime(2026, 8, 1, 9, 0))
    assert table.opened_at is not None
''',
        ),
    ],
    "reports": [
        (
            "test_revenue_summary_empty",
            '''def test_revenue_summary_empty():
    summary = revenue_summary([])
    assert summary["bills"] == 0
    assert summary["average"] == 0
''',
        ),
    ],
}

# README sections appended by the update_readme op.
README_SECTIONS: list[tuple[str, str]] = [
    (
        "## Troubleshooting",
        "If the CLI cannot write to `~/.poolhall/`, make sure the directory is\n"
        "writable or point `DATA_FILE` in `poolhall/config.py` somewhere else.\n",
    ),
    (
        "## Roadmap",
        "- [ ] Automatic daily report email\n"
        "- [ ] Export reservations to calendar format\n"
        "- [ ] Loyalty program with stored credit\n",
    ),
    (
        "## Development",
        "Clone the repository, install in editable mode (`pip install -e .`) and run\n"
        "the test suite with `python -m pytest`. The CLI is a thin layer over the\n"
        "`poolhall` package, so most logic is unit-testable without a terminal.\n",
    ),
    (
        "## Configuration reference",
        "| Setting | Default | Meaning |\n"
        "| --- | --- | --- |\n"
        "| `OPENING_HOUR` | 9 | Hall opens at this hour |\n"
        "| `CLOSING_HOUR` | 23 | Hall closes at this hour |\n"
        "| `DEFAULT_RATE_PER_HOUR` | 60000 | Hourly rate in VND |\n"
        "| `VAT_RATE` | 0.08 | VAT applied on bills |\n",
    ),
]

# Brand-new modules created by the new_module op (rare).
NEW_MODULES: dict[str, str] = {
    "poolhall/export.py": '''\
"""Export pool hall data to CSV files."""

from __future__ import annotations

import csv
import io
from typing import Iterable


def to_csv(rows: Iterable[dict], fieldnames: list[str]) -> str:
    """Render a list of dicts as a CSV string."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def export_inventory(items, path: str) -> int:
    """Write inventory rows to a CSV file, returning the row count."""
    rows = [
        {"name": item.name, "quantity": item.quantity, "unit_price": item.unit_price}
        for item in items
    ]
    text = to_csv(rows, ["name", "quantity", "unit_price"])
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return len(rows)
''',
    "poolhall/notifications.py": '''\
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
''',
}

# Generic test-suite skeleton used by the new_test_module op.
NEW_TEST_TEMPLATE = '''\
"""Tests for the {module} module."""

from __future__ import annotations

import poolhall.{module} as mod


def test_module_imports():
    assert mod.__name__ == "poolhall.{module}"


def test_public_api_surface():
    for name in {names}:
        assert callable(getattr(mod, name)), f"missing {{name}}"
'''
