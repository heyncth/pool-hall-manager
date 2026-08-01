"""Orchestrator for the Repository Evolution Engine.

Pipeline: timeline -> planner -> mutation -> compile gate -> message -> git
Each module answers exactly one question; this file only wires them together.
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import bootstrap  # noqa: E402
import git  # noqa: E402
import message  # noqa: E402
import mutation  # noqa: E402
import planner  # noqa: E402
import timeline  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ZONE_MARKER = Path("poolhall") / "__init__.py"


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timeline.LOCAL_TZ)


def _derive_seed(day: datetime, head_hash: str, explicit: int | None) -> int:
    if explicit is not None:
        return explicit
    return (day.toordinal() << 8) ^ int((head_hash or "0")[:8], 16)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repository Evolution Engine")
    parser.add_argument("--repo", default=str(REPO_ROOT), help="repository root (default: this repo)")
    parser.add_argument("--date", default=None, help="simulate a specific day, YYYY-MM-DD")
    parser.add_argument("--seed", type=int, default=None, help="override the PRNG seed")
    parser.add_argument("--max-commits", type=int, default=None, help="force a commit count")
    parser.add_argument("--dry-run", action="store_true", help="plan changes without committing")
    parser.add_argument("--no-push", action="store_true", help="do not push after committing")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    day = _parse_date(args.date) if args.date else timeline.local_now()
    head_hash = git.head_short_hash(repo)
    rng = random.Random(_derive_seed(day, head_hash, args.seed))

    if not (repo / ZONE_MARKER).exists():
        if args.dry_run:
            print("  bootstrap would run (no poolhall/ package yet)")
        else:
            print("  bootstrapping ported project...")
            bootstrap.run(repo, day)
            head_hash = git.head_short_hash(repo)

    count = args.max_commits if args.max_commits is not None else timeline.pick_commit_count(rng, day)
    times = timeline.commit_times(rng, count, day)
    print(f"  day {day.date().isoformat()} -> {count} commits")

    recent_commits = git.recent_commits(repo, 30)
    recent_messages = [c["subject"] for c in recent_commits]
    recent_types = [m.split("(")[0].split(":")[0].strip() for m in recent_messages]
    recent_files = git.recent_files(repo, 30)
    touched_today: list[str] = []
    made = 0

    for when in times:
        snapshot = _snapshot(repo)
        change = None
        for _ in range(4):
            change = planner.plan(rng, repo, recent_files, recent_types, touched_today)
            if change is not None and _gate(repo, change):
                break
            if change is not None:
                _rollback(repo, snapshot, change)
            change = None
        if change is None:
            continue
        subject = message.make(rng, change.op, change.module, change.name, change.detail, change.version, recent_messages)
        if args.dry_run:
            print(f"  [dry-run] {when:%H:%M} {change.op:<18} {subject}  ({', '.join(str(f) for f in change.files)})")
            _rollback(repo, snapshot, change)  # dry-run must not touch the tree
            made += 1
            continue
        result = git.commit(repo, change.files, subject, when)
        if result != "ok":
            continue
        print(f"  {when:%H:%M} {subject}")
        made += 1
        recent_messages = recent_messages[-29:] + [subject]
        recent_types = recent_types[-9:] + [message.type_of(change.op)]
        touched_today.extend(str(f) for f in change.files)
        recent_files = [f for f in recent_files if f not in touched_today] + touched_today

    print(f"  {made}/{count} committed")
    if made and not args.dry_run and not args.no_push:
        git.push(repo)
    return 0


def _gate(repo: Path, change: mutation.Change) -> bool:
    """Compile gate: every changed .py file must be syntactically valid."""
    for rel in change.files:
        if rel.suffix != ".py":
            continue
        path = repo / rel
        if not path.exists():
            return False
        if not git.compile_ok(path):
            print(f"  ! compile gate failed for {rel}, skipping")
            return False
    return True


def _snapshot(repo: Path) -> dict:
    """Snapshot all zone file contents so failed mutations can be rolled back."""
    snap: dict = {}
    for rel in mutation.zone_py_files(repo):
        path = repo / rel
        if path.exists():
            snap[rel] = path.read_text(encoding="utf-8")
    for rel in (Path("README.md"), Path("pyproject.toml")):
        path = repo / rel
        if path.exists():
            snap[rel] = path.read_text(encoding="utf-8")
    return snap


def _rollback(repo: Path, snapshot: dict, change: mutation.Change) -> None:
    """Undo a mutation that failed the compile gate (spec: fail -> rollback)."""
    for rel in change.files:
        path = repo / rel
        if rel not in snapshot and path.exists():
            path.unlink()  # newly created file
    for rel, content in snapshot.items():
        (repo / rel).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
