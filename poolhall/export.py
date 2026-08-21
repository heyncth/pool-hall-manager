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
