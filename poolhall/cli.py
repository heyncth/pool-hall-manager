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
    """
    Entry point for the ``poolhall`` console script.

    Args:
        argv: Description.

    Returns:
        Description.
    """
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
