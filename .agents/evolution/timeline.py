"""When commits happen: day mood, clusters and jitter.

Answers the single question: *"on a given day, how many commits and at what
times?"* Times are generated in the operator's local timezone (UTC+7) and
formatted with an explicit offset so the day shown on the contribution graph
is stable whether the engine runs locally or on GitHub Actions.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

LOCAL_OFFSET = timedelta(hours=7)
LOCAL_TZ = timezone(LOCAL_OFFSET, name="ICT")

# Mood -> (weight, {commit_count: probability}). Non-uniform on purpose:
# a real developer rarely has flat probabilities.
MOODS: list[tuple[str, float, dict[int, float]]] = [
    ("lazy", 0.55, {0: 0.25, 1: 0.30, 2: 0.25, 3: 0.20}),
    ("normal", 0.35, {2: 0.15, 3: 0.25, 4: 0.30, 5: 0.20, 6: 0.10}),
    ("busy", 0.10, {6: 0.10, 7: 0.20, 8: 0.30, 9: 0.25, 10: 0.15}),
]

START_HOUR = 8
END_HOUR = 23


def local_now() -> datetime:
    """Current time in the operator's local timezone."""
    return datetime.now(LOCAL_TZ)


def start_of_day(day: datetime) -> datetime:
    """Return midnight of ``day`` in the local timezone."""
    return day.replace(hour=0, minute=0, second=0, microsecond=0)


def pick_commit_count(rng: random.Random, day: datetime) -> int:
    """Choose how many commits the developer makes on ``day``."""
    name = _pick_mood(rng)
    mood = next(m for m in MOODS if m[0] == name)
    count = _sample_pmf(rng, mood[2])
    if day.weekday() >= 5:  # weekend: leaner, sometimes skipped
        count = rng.choice([0, 0, int(count * 0.5), count])
    return count


def commit_times(rng: random.Random, count: int, day: datetime) -> list[datetime]:
    """Generate ``count`` timestamps clustered across the working day."""
    if count <= 0:
        return []
    available = (END_HOUR - START_HOUR) * 60
    num_clusters = max(1, min(available, count // rng.randint(2, 4)))
    centers = sorted(rng.sample(range(available), num_clusters))
    weights = [rng.randint(1, 10) for _ in range(num_clusters)]
    assignments = rng.choices(range(num_clusters), weights=weights, k=count)

    times: list[datetime] = []
    base = day.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    for idx in assignments:
        spread = rng.choice([3, 5, 8, 12, 20])
        jitter = rng.randint(-spread, spread)
        minutes = max(0, min(available - 1, centers[idx] + jitter))
        times.append(base + timedelta(minutes=minutes))
    times.sort()
    return times


def git_date(dt: datetime) -> str:
    """Format a datetime for GIT_AUTHOR_DATE / GIT_COMMITTER_DATE."""
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def _pick_mood(rng: random.Random) -> str:
    names = [m[0] for m in MOODS]
    weights = [m[1] for m in MOODS]
    return rng.choices(names, weights=weights, k=1)[0]


def _sample_pmf(rng: random.Random, pmf: dict[int, float]) -> int:
    values = list(pmf.keys())
    weights = list(pmf.values())
    return rng.choices(values, weights=weights, k=1)[0]
