"""When commits happen: yearly mood chain, sessions and jitter.

Answers the single question: *"on a given day, how many commits and at what
times?"* Days are drawn from a seeded full-year state chain (idle / flow /
crunch / rest plus vacation blocks), so activity clusters, burns out and
takes holidays the way a human year does. Times are generated as work
sessions inside the operator's local timezone (UTC+7) and formatted with an
explicit offset so the day shown on the contribution graph is stable whether
the engine runs locally or on GitHub Actions.
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

LOCAL_OFFSET = timedelta(hours=7)
LOCAL_TZ = timezone(LOCAL_OFFSET, name="ICT")

# Year state chain. Seeded from the year alone (never the day or HEAD) so
# yesterday's state stays stable while the repository moves forward.
TRANSITIONS: dict[str, list[tuple[str, float]]] = {
    "idle": [("idle", 0.70), ("flow", 0.25), ("crunch", 0.03), ("rest", 0.02)],
    "flow": [("flow", 0.80), ("idle", 0.14), ("crunch", 0.04), ("rest", 0.02)],
    # stays until CRUNCH_RUN_MIN (guarded below), then exits only into rest (burnout dip)
    "crunch": [("crunch", 0.45), ("rest", 0.55)],
}
CRUNCH_RUN_MIN = 2          # crunch stays at least this long
CRUNCH_RUN_MAX = 5          # ... and always ends (then rest: burnout dip)
REST_RUN_MAX = 4
VACATION_BLOCKS = (1, 2)    # forced gaps of VACATION_DAYS per year
VACATION_DAYS = (3, 14)
CHAIN_EPOCH_YEAR = 2024     # fixed origin so the chain never depends on HEAD

# Commits per state. Crunch ramps: warm-up day, hot days, wind-down day.
COUNT_PMFS: dict[str, dict[int, float]] = {
    "rest": {0: 1.0},
    "idle": {0: 0.40, 1: 0.30, 2: 0.20, 3: 0.10},
    "flow": {1: 0.15, 2: 0.25, 3: 0.25, 4: 0.20, 5: 0.10, 6: 0.05},
}
CRUNCH_RAMP: dict[int, tuple[int, int]] = {
    1: (8, 16),
    5: (6, 12),   # wind-down right before the rest dip
}
CRUNCH_HOT = (15, 40)

# Work sessions: peaks avoid the meal troughs (12:00-13:30, 17:30-19:59) and
# are mutually separated by the deep-work gaps a real day has.
PEAKS: tuple[tuple[float, float], ...] = ((9.0, 11.5), (14.0, 17.0), (20.0, 23.9))
TROUGHS: tuple[tuple[float, float], ...] = ((12.0, 13.5), (17.5, 19.99))
WEEKEND_SKIP_P = 0.45       # weekends are leaner unless a crunch is running


def local_now() -> datetime:
    """Current time in the operator's local timezone."""
    return datetime.now(LOCAL_TZ)


def start_of_day(day: datetime) -> datetime:
    """Return midnight of ``day`` in the local timezone."""
    return day.replace(hour=0, minute=0, second=0, microsecond=0)


@lru_cache(maxsize=4)
def year_days(year: int) -> dict[date, tuple[str, int]]:
    """Full-year chain: date -> (state, run-length). Seeded from ``year`` only."""
    rng = random.Random(year * 7919 + CHAIN_EPOCH_YEAR)
    vacations: set[date] = set()
    for _ in range(rng.randint(*VACATION_BLOCKS)):
        base = date(year, 1, 1) + timedelta(days=rng.randint(0, 340))
        for offset in range(rng.randint(*VACATION_DAYS)):
            vacations.add(base + timedelta(days=offset))

    days: dict[date, tuple[str, int]] = {}
    state = "idle"
    run = 0
    rest_target = 1
    current = date(year, 1, 1)
    while current.year == year:
        if current in vacations:
            state, rest_target = "rest", 0  # rest_target 0 -> resume the day after
            days[current] = ("rest", 0)
        else:
            if state == "crunch" and run >= CRUNCH_RUN_MAX:
                state, run = "rest", 0
                rest_target = rng.randint(2, REST_RUN_MAX)
            elif state == "rest" and run >= rest_target:
                state, run = "idle", 0
            elif state in TRANSITIONS and run >= (CRUNCH_RUN_MIN if state == "crunch" else 1):
                nxt = _weighted_pick(rng, TRANSITIONS[state])
                if nxt != state:
                    state, run = nxt, 0
                    if state == "rest":
                        rest_target = rng.randint(1, REST_RUN_MAX)
            run += 1
            days[current] = (state, run)
        current += timedelta(days=1)
    return days


def pick_commit_count(rng: random.Random, day: datetime) -> int:
    """Choose how many commits the developer makes on ``day``."""
    state, run = year_days(day.year).get(day.date(), ("idle", 1))
    if state == "crunch":
        count = _crunch_count(rng, run)
    else:
        count = _sample_pmf(rng, COUNT_PMFS[state])
    if day.weekday() >= 5 and state != "crunch":
        # weekend: leaner, sometimes skipped (a crunch deadline overrides it)
        count = rng.choice([0, 0, int(count * 0.5), count])
    return count


def commit_times(rng: random.Random, count: int, day: datetime) -> list[datetime]:
    """Generate ``count`` timestamps as 1-3 work sessions across the day."""
    if count <= 0:
        return []
    if count <= 3:
        session_count = 1
    elif count <= 8:
        session_count = rng.choice([1, 2])
    else:
        session_count = rng.choice([2, 3])
    session_count = min(session_count, len(PEAKS))
    windows = sorted(rng.sample(list(PEAKS), session_count))

    # distribute the day's commits across the chosen sessions, remainder last
    shares = [count // session_count] * session_count
    for index in range(count % session_count):
        shares[index] += 1

    times: list[datetime] = []
    for (window, share) in zip(windows, shares):
        if share <= 0:
            continue
        window_start = int(window[0] * 60)
        window_end = min(int(window[1] * 60), 23 * 60 + 59)
        span = window_end - window_start
        # a session burns ~8.5 min per commit; compress gaps when the window is tight
        gap_hi = max(2, min(15, span // max(1, share)))
        latest_start = max(window_start, window_end - share * gap_hi)
        minute = rng.randint(window_start, latest_start)
        for _ in range(share):
            minute = min(minute, window_end)
            times.append(
                day.replace(hour=minute // 60, minute=minute % 60,
                            second=rng.randint(0, 59), microsecond=0)
            )
            minute += rng.randint(2, gap_hi)
    times.sort()
    return times


def git_date(dt: datetime) -> str:
    """Format a datetime for GIT_AUTHOR_DATE / GIT_COMMITTER_DATE."""
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def _crunch_count(rng: random.Random, run: int) -> int:
    lo, hi = CRUNCH_RAMP.get(run, CRUNCH_HOT)
    return rng.randint(lo, hi)


def _weighted_pick(rng: random.Random, transitions: list[tuple[str, float]]) -> str:
    names = [name for name, _ in transitions]
    weights = [weight for _, weight in transitions]
    return rng.choices(names, weights=weights, k=1)[0]


def _sample_pmf(rng: random.Random, pmf: dict[int, float]) -> int:
    values = list(pmf.keys())
    weights = list(pmf.values())
    return rng.choices(values, weights=weights, k=1)[0]
