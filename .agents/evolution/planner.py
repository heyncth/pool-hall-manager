"""The probability engine: chooses what to change next.

Answers the single question: *"which file and operation for this commit?"*
Selection is weighted, adapts to the current repository (fewer new files as
the project matures), avoids touching the same file twice in a row and avoids
running the same commit type four times consecutively.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import message  # noqa: E402
import mutation  # noqa: E402

MAX_FILES = 40  # new files are no longer created at this size
TYPE_STREAK_LIMIT = 3  # never run the same commit type 4 times in a row


def plan(rng: random.Random, repo: Path, recent_files: list[str], recent_types: list[str], touched_today: list[str]) -> mutation.Change | None:
    """Produce one change, or None when nothing is applicable right now."""
    zone = mutation.zone_py_files(repo)

    if rng.random() < 0.12:
        change = _try_meta(rng, repo, zone, recent_types)
        if change is not None:
            return change

    for _ in range(3):
        rel = _pick_file(rng, zone, recent_files, touched_today)
        if rel is None:
            return None
        change = _try_file_ops(rng, repo, rel, recent_types)
        if change is not None:
            return change
    return None


def _try_meta(rng: random.Random, repo: Path, zone: list[Path], recent_types: list[str]) -> mutation.Change | None:
    names = list(mutation.META_WEIGHTS)
    if len(zone) >= MAX_FILES:
        names = [n for n in names if n not in ("new_module", "new_test_module")]
    if not names:
        return None
    weights = [mutation.META_WEIGHTS[n] for n in names]
    for _ in range(len(names)):
        op = rng.choices(names, weights=weights, k=1)[0]
        idx = names.index(op)
        names.pop(idx)
        weights.pop(idx)
        if _would_streak(op, recent_types):
            continue
        change = mutation.try_meta_op(repo, rng, op)
        if change is not None:
            return change
    return None


def _try_file_ops(rng: random.Random, repo: Path, rel: Path, recent_types: list[str]) -> mutation.Change | None:
    names = list(mutation.FILE_WEIGHTS)
    weights = [mutation.FILE_WEIGHTS[n] for n in names]
    for _ in range(len(names)):
        op = rng.choices(names, weights=weights, k=1)[0]
        idx = names.index(op)
        names.pop(idx)
        weights.pop(idx)
        if _would_streak(op, recent_types):
            continue
        change = mutation.try_file_op(repo, rng, op, rel)
        if change is not None:
            return change
    return None


def _pick_file(rng: random.Random, zone: list[Path], recent_files: list[str], touched_today: list[str]) -> Path | None:
    if not zone:
        return None
    recent = set(recent_files[:10]) | set(touched_today)
    names = [str(f) for f in zone]
    weights = [1 if name in recent else 4 for name in names]
    return Path(rng.choices(names, weights=weights, k=1)[0])


def _would_streak(op: str, recent_types: list[str]) -> bool:
    """True when picking ``op`` would make the same commit type 4x in a row."""
    if len(recent_types) < TYPE_STREAK_LIMIT:
        return False
    ctype = message.type_of(op)
    tail = [t for t in recent_types if t]
    return len(tail) >= TYPE_STREAK_LIMIT and all(t == ctype for t in tail[-TYPE_STREAK_LIMIT:])
