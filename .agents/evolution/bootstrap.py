"""One-time bootstrap: the "ported from Java" commit history.

Writes the hand-authored pool hall package from :mod:`library` and creates a
sequence of realistic commits spread over the past couple of weeks, ending
with the removal of the legacy Java Swing prototype. Runs once — later runs
of the engine only evolve what exists. Idempotent: does nothing when the
``poolhall`` package is already present.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))

import git  # noqa: E402
import library  # noqa: E402
import timeline  # noqa: E402

# (days ago, HH:MM, message, files) — files are PACKAGE keys, or "REMOVE_SRC".
SEQUENCE: list[tuple[int, str, str, list[str]]] = [
    (15, "14:20", "feat: scaffold poolhall package and build config",
     ["pyproject.toml", "poolhall/__init__.py"]),
    (14, "10:05", "feat: add configuration and shared utilities",
     ["poolhall/config.py", "poolhall/utils.py"]),
    (13, "15:40", "feat(models): add table, reservation and stock models",
     ["poolhall/models.py"]),
    (12, "09:30", "feat(pricing): add hourly pricing and rounding rules",
     ["poolhall/pricing.py"]),
    (11, "17:10", "feat(storage): add atomic json persistence",
     ["poolhall/storage.py"]),
    (10, "13:55", "feat(billing): add session billing with vat and discounts",
     ["poolhall/billing.py"]),
    (9, "19:25", "feat(tables): add table registry and reservations",
     ["poolhall/tables.py"]),
    (8, "11:15", "feat(inventory): add stock tracking",
     ["poolhall/inventory.py"]),
    (7, "16:45", "feat(reports): add daily and revenue reports",
     ["poolhall/reports.py"]),
    (6, "20:05", "test: cover core modules with unit tests",
     sorted(library.TESTS)),
    (5, "12:30", "feat(cli): add command-line interface",
     ["poolhall/cli.py"]),
    (4, "21:00", "docs: document usage and configuration",
     ["README.md"]),
    (3, "14:10", "refactor: drop legacy Java Swing prototype",
     ["REMOVE_SRC"]),
    (2, "18:30", "chore: add daily evolution tooling",
     [".agents/evolution", ".github/workflows/daily-sync.yml"]),
]


def run(repo: Path, today: datetime) -> bool:
    """Create the port history. Safe to call repeatedly."""
    if (repo / "poolhall" / "__init__.py").exists():
        return True

    for rel, content in library.PACKAGE.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    for offset_days, hhmm, message_text, files in SEQUENCE:
        hour, minute = (int(x) for x in hhmm.split(":"))
        when = (today - timedelta(days=offset_days)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        if files == ["REMOVE_SRC"]:
            if (repo / "src").exists():
                git.remove(repo, "src", when)
            continue
        rels = [Path(f) for f in files]
        result = git.commit(repo, rels, message_text, when)
        print(f"  {when:%m-%d %H:%M} {message_text} -> {result}")

    return True
