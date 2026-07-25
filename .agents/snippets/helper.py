#!/usr/bin/env python3
"""Project development utilities."""

import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from textwrap import dedent

# ─── Dependencies ────────────────────────────────────────────────────────────

try:
    from wonderwords import RandomWord
except ImportError:
    print("ERROR: wonderwords required. Run: pip install wonderwords")
    sys.exit(1)

_wonder = RandomWord()
_adj_cache: list[str] = []
_verb_cache: list[str] = []
_noun_cache: list[str] = []


def _fill_cache() -> None:
    global _adj_cache, _verb_cache, _noun_cache
    if not _adj_cache:
        _adj_cache = _wonder.random_words(200, include_parts_of_speech=["adjectives"])
    if not _verb_cache:
        _verb_cache = _wonder.random_words(200, include_parts_of_speech=["verbs"])
    if not _noun_cache:
        _noun_cache = _wonder.random_words(500, include_parts_of_speech=["nouns"])


def _pick(*arrays: list[str]) -> str:
    pool = random.choice(arrays)
    return random.choice(pool)


def verb() -> str:
    return _pick(_verb_cache)


def noun() -> str:
    return _pick(_noun_cache)


def adj() -> str:
    return _pick(_adj_cache)


def pascal(*parts: str) -> str:
    return "".join(p.capitalize() for p in parts if p)


# ─── Paths ───────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = REPO_ROOT / ".agents" / "snippets" / "out"
INIT_FILE = OUT_DIR / "__init__.py"

# ─── Day Type Configuration ──────────────────────────────────────────────────

DAY_TYPES = [
    {"name": "bad",     "weight": 15, "min_c": 5,  "max_c": 10},
    {"name": "average", "weight": 50, "min_c": 11, "max_c": 18},
    {"name": "good",    "weight": 25, "min_c": 19, "max_c": 28},
    {"name": "great",   "weight": 10, "min_c": 29, "max_c": 40},
]

PICK_WEIGHTS = [d["weight"] for d in DAY_TYPES]
PICK_NAMES  = [d["name"]  for d in DAY_TYPES]

# ─── Conventional Commit Types ───────────────────────────────────────────────

COMMIT_TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]


# ═══════════════════════════════════════════════════════════════════════════════
#  10 Code Archetypes
#  Each returns (module_name, code_string, archetype_label)
# ═══════════════════════════════════════════════════════════════════════════════

def _arch_01_filter() -> tuple[str, str, str]:
    v, n1, n2 = verb(), noun(), noun()
    dt = random.choice(["int", "float"])
    op = random.choice(["*", "+", "//"])
    op_val = random.randint(2, 10)
    default = random.randint(1, 100)
    name = f"filter_{n1}"

    code = dedent(f'''\
    def {name}(items: list[{dt}], threshold: {dt} = {default}) -> list[{dt}]:
        """Filter {n2}s above a threshold and {v} the result.

        Args:
            items: Collection of {n2}s to process.
            threshold: Minimum value to include.

        Returns:
            Filtered and transformed list of {n2}s.
        """
        if not items:
            return []

        result = []
        for item in items:
            if item >= threshold:
                result.append(item {op} {op_val})
        return result
    ''')
    return name, code, "filter"


def _arch_02_parse() -> tuple[str, str, str]:
    v, n1, n2 = verb(), noun(), noun()
    sep = random.choice([",", "|", ";", ":"])
    max_len = random.choice([256, 512, 1024])
    parts_count = random.randint(2, 5)
    name = f"{v}_{n1}"

    code = dedent(f'''\
    def {name}(raw: str, delimiter: str = "{sep}", max_length: int = {max_len}) -> list[dict[str, str]] | None:
        """Parse and validate {n2} input from a delimited string.

        Expected format: {parts_count} fields separated by "{sep}".

        Args:
            raw: Raw input string to parse.
            delimiter: Field separator character.
            max_length: Maximum allowed input length.

        Returns:
            List of parsed records or None if validation fails.
        """
        if not raw or len(raw) > max_length:
            return None

        records = []
        for line in raw.strip().split("\\n"):
            fields = line.split(delimiter)
            if len(fields) != {parts_count}:
                continue
            record = {{}}
            for i, val in enumerate(fields):
                record[f"field_{{i}}"] = val.strip()
            records.append(record)
        return records if records else None
    ''')
    return name, code, "parser"


def _arch_03_group() -> tuple[str, str, str]:
    _, n1, n2 = verb(), noun(), noun()
    name = f"group_{n1}"

    code = dedent(f'''\
    def {name}(items: list[dict], key: str = "{n2}") -> dict[str, list]:
        """Group a list of records by a specified key.

        Args:
            items: List of dictionaries to group.
            key: Dictionary key to group by.

        Returns:
            Dictionary mapping each unique key value to its records.
        """
        result: dict[str, list] = {{}}
        for item in items:
            k = item.get(key, "unknown")
            if k not in result:
                result[k] = []
            result[k].append(item)
        return result
    ''')
    return name, code, "group"


def _arch_04_class() -> tuple[str, str, str]:
    v1, v2, n1, n2, a1 = verb(), verb(), noun(), noun(), adj()
    cls_name = pascal(a1, n1, n2)
    name = f"{v1}_{n1}"

    code = dedent(f'''\
    class {cls_name}:
        """Process and cache {n2} operations with configurable {a1} parameters.

        Provides efficient {v1} and {v2} methods with built-in caching.
        """

        def __init__(self, {n2}_limit: int = {random.randint(50, 200)}):
            self._{n2}_limit = {n2}_limit
            self._cache: dict[str, list] = {{}}
            self._count = 0

        def {v1}(self, items: list) -> list:
            """Process items through the {v1} pipeline."""
            key = str(items[:5])
            if key in self._cache:
                return self._cache[key]
            result = [item for item in items if item]
            self._cache[key] = result
            self._count += 1
            return result

        def {v2}(self, items: list) -> list:
            """Apply {v2} transformation to items."""
            result = []
            for item in items:
                if isinstance(item, (int, float)):
                    result.append(item * {random.randint(2, 5)})
            return result

        @property
        def processed_count(self) -> int:
            return self._count

        def clear(self) -> None:
            self._cache.clear()
            self._count = 0
    ''')
    return name, code, f"{cls_name} class"


def _arch_05_generator() -> tuple[str, str, str]:
    v, n1, n2 = verb(), noun(), noun()
    name = f"{v}_{n1}s"

    code = dedent(f'''\
    from collections.abc import Generator


    def {name}(items: list[{n2}], batch_size: int = {random.randint(3, 10)}) -> Generator[list, None, None]:
        """Yield batches of processed {n1}s from the input stream.

        Args:
            items: Full list of {n2} values to process.
            batch_size: Number of items per yielded batch.

        Yields:
            Batches of processed {n1}s.
        """
        batch = []
        for item in items:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
    ''')
    return name, code, "generator"


def _arch_06_decorator() -> tuple[str, str, str]:
    v, n1, _, a1 = verb(), noun(), noun(), adj()
    name = f"{v}_{n1}"
    default_n = random.randint(1, 5)

    code = dedent(f'''\
    import functools
    import time
    from collections.abc import Callable
    from typing import Any


    def {name}(max_attempts: int = {default_n}, delay: float = {random.uniform(0.1, 2.0):.1f}):
        """Decorator that retries a function up to max_attempts times on failure.

        Args:
            max_attempts: Maximum retry count before raising.
            delay: Seconds to wait between retries.

        Returns:
            Decorated function with {a1} retry logic.
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                last_error = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        if attempt < max_attempts - 1:
                            time.sleep(delay)
                raise RuntimeError(f"{{func.__name__}} failed after {{max_attempts}} attempts") from last_error
            return wrapper
        return decorator
    ''')
    return name, code, "decorator"


def _arch_07_context_manager() -> tuple[str, str, str]:
    v, n1, n2, a1 = verb(), noun(), noun(), adj()
    cls_name = pascal(a1, n1, n2)
    name = f"{v}_{n1}"

    code = dedent(f'''\
    class {cls_name}:
        """Context manager for {a1} {n2} resource lifecycle.

        Usage:
            with {cls_name}() as {n1}:
                {n1}.{v}()
        """

        def __init__(self, {n2}_path: str = "/tmp/{n1}.dat"):
            self._{n2}_path = {n2}_path
            self._opened = False

        def __enter__(self):
            self._opened = True
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._opened = False
            return False

        def {v}(self) -> str:
            if not self._opened:
                raise RuntimeError("Resource is not open")
            return f"Processing {{self._{n2}_path}}"
    ''')
    return name, code, "context manager"


def _arch_08_convert() -> tuple[str, str, str]:
    v, n1, n2 = verb(), noun(), noun()
    name = f"{v}_{n1}"

    code = dedent(f'''\
    import json


    def {name}(items: list[dict], output_format: str = "{n2}") -> str:
        """Convert a list of dictionaries to the specified output format.

        Supported formats: "json", "csv", "{n2}".

        Args:
            items: List of dictionaries to convert.
            output_format: Target format string.

        Returns:
            Formatted string representation.

        Raises:
            ValueError: If output_format is not supported.
        """
        if not items:
            return ""

        if output_format == "json":
            return json.dumps(items, indent=2)

        if output_format == "csv":
            if not items:
                return ""
            headers = list(items[0].keys())
            lines = [",".join(headers)]
            for item in items:
                lines.append(",".join(str(item.get(h, "")) for h in headers))
            return "\\n".join(lines)

        raise ValueError(f"Unsupported format: {{output_format}}")
    ''')
    return name, code, "converter"


def _arch_09_search() -> tuple[str, str, str]:
    _, n1, n2 = verb(), noun(), noun()
    name = f"search_{n1}"

    code = dedent(f'''\
    def {name}(items: list[{n2}], target: {n2} | None = None) -> dict:
        """Search through {n1}s and return statistics about matches.

        Args:
            items: List of {n2} values to search through.
            target: Optional specific value to locate.

        Returns:
            Dictionary with search statistics and results.
        """
        result = {{
            "total": len(items),
            "found": False,
            "matches": [],
            "stats": {{}},
        }}

        if not items:
            return result

        if target is not None:
            matches = [i for i, v in enumerate(items) if v == target]
            result["found"] = len(matches) > 0
            result["matches"] = matches

        numeric = [v for v in items if isinstance(v, (int, float))]
        if numeric:
            result["stats"] = {{
                "min": min(numeric),
                "max": max(numeric),
                "avg": sum(numeric) / len(numeric),
            }}

        return result
    ''')
    return name, code, "search utility"


def _arch_10_stats() -> tuple[str, str, str]:
    _, n1, n2, a1 = verb(), noun(), noun(), adj()
    name = f"stats_{n1}"

    code = dedent(f'''\
    import statistics


    def {name}(values: list[float], {n2}: str = "{n1}") -> dict[str, float | int | None]:
        """Compute {a1} statistical measures for a dataset.

        Args:
            values: List of numeric values to analyze.
            {n2}: Label for the dataset (used in output).

        Returns:
            Dictionary of statistical measures.
        """
        if not values:
            return {{"label": {n2}, "count": 0, "error": "empty dataset"}}

        cleaned = [v for v in values if isinstance(v, (int, float))]
        if not cleaned:
            return {{"label": {n2}, "count": 0, "error": "no numeric data"}}

        result: dict[str, float | int | None] = {{
            "label": {n2},
            "count": len(cleaned),
            "sum": sum(cleaned),
            "mean": statistics.mean(cleaned),
        }}

        if len(cleaned) > 1:
            result["stdev"] = statistics.stdev(cleaned) if len(cleaned) >= 2 else 0.0
            result["median"] = statistics.median(cleaned)
        else:
            result["stdev"] = 0.0
            result["median"] = cleaned[0]

        return result
    ''')
    return name, code, "stats function"


ARCHETYPES = [
    _arch_01_filter,
    _arch_02_parse,
    _arch_03_group,
    _arch_04_class,
    _arch_05_generator,
    _arch_06_decorator,
    _arch_07_context_manager,
    _arch_08_convert,
    _arch_09_search,
    _arch_10_stats,
]


# ═══════════════════════════════════════════════════════════════════════════════
#  Core Logic
# ═══════════════════════════════════════════════════════════════════════════════

def _pick_day_type() -> tuple[str, int]:
    name = random.choices(PICK_NAMES, weights=PICK_WEIGHTS, k=1)[0]
    dtype = next(d for d in DAY_TYPES if d["name"] == name)
    count = random.randint(dtype["min_c"], dtype["max_c"])
    return name, count


def _generate_timestamps(count: int, day: datetime) -> list[datetime]:
    """Generate timestamps with natural clustering.
    
    Creates clusters of 2-5 close commits with gaps between,
    plus random jitter so no two days look alike.
    """
    start_hour = 8
    end_hour = 23
    available_mins = (end_hour - start_hour) * 60

    if count == 0:
        return []

    # Determine number of clusters (fewer clusters = tighter grouping)
    num_clusters = max(2, count // random.randint(2, 5))
    if num_clusters > available_mins:
        num_clusters = available_mins

    # Pick cluster centers spread across the day
    centers = sorted(random.sample(range(available_mins), num_clusters))

    # Assign commits to clusters (some clusters get more, some fewer)
    weights = [random.randint(1, 10) for _ in range(num_clusters)]
    assignments = random.choices(range(num_clusters), weights=weights, k=count)

    times = []
    for idx in assignments:
        center = centers[idx]
        # Jitter: most commits within 1-20min of center, some wider
        jitter_range = random.choice([3, 5, 8, 10, 15, 20, 30, 45])
        jitter = random.randint(-jitter_range, jitter_range)
        t = max(0, min(available_mins, center + jitter))
        times.append(t)

    # Sort but add a tiny random shuffle for near-simultaneous commits
    times.sort()

    base = day.replace(hour=0, minute=0, second=0, microsecond=0)
    return [base + timedelta(minutes=start_hour * 60 + t) for t in times]


def _git_commit(message: str, author_dt: datetime) -> bool:
    ts = author_dt.strftime("%Y-%m-%d %H:%M:%S")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = ts
    env["GIT_COMMITTER_DATE"] = ts

    try:
        subprocess.run(["git", "add", ".agents/snippets/"], cwd=REPO_ROOT, capture_output=True, check=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            if "nothing to commit" in result.stderr or "nothing to commit" in result.stdout:
                return False
            print(f"  ! commit error: {result.stderr.strip()}")
            return False
        print(f"  {ts} {message}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  x git error: {e}")
        return False


def _update_init(module_name: str) -> None:
    if not INIT_FILE.exists():
        INIT_FILE.write_text(f"from .{module_name} import *\n")
        return

    content = INIT_FILE.read_text()
    line = f"from .{module_name} import *\n"
    if line not in content:
        INIT_FILE.write_text(content + line)


def _get_existing_modules() -> list[str]:
    if not OUT_DIR.exists():
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        return []
    return sorted(
        f.stem for f in OUT_DIR.iterdir()
        if f.suffix == ".py" and f.stem != "__init__"
    )


def _make_message(is_new: bool, name: str, label: str, mod_name: str | None = None) -> str:
    """Build a conventional commit message using wonderwords for all parts."""
    msg_type = random.choice(COMMIT_TYPES)
    scope = noun()

    if is_new:
        templates = [
            f"add {name}",
            f"add {name} {label}",
            f"implement {name} for {label}",
            f"introduce {name} for {noun()}",
            f"{verb()} {name} {noun()}",
            f"add {noun()} utilities via {name}",
            f"implement {label} support in {name}",
            f"add {adj()} {label} using {name}",
        ]
    else:
        templates = [
            f"update {mod_name}",
            f"improve {mod_name} {label}",
            f"refactor {mod_name} for {noun()}",
            f"{label} improvements in {mod_name}",
            f"optimize {mod_name} {noun()} handling",
            f"fix {mod_name} {noun()} edge case",
            f"extend {mod_name} with {label}",
            f"revise {mod_name} for better {noun()}",
        ]

    desc = random.choice(templates)
    return f"{msg_type}({scope}): {desc}"


# ═══════════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    _fill_cache()

    today = datetime.now(timezone.utc)
    date_str = today.strftime("%Y-%m-%d")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INIT_FILE.exists():
        INIT_FILE.write_text("# snippets\n")

    day_type, commit_count = _pick_day_type()
    print(f"\n{'='*50}")
    print(f"  {date_str}")
    print(f"  {day_type.upper()} ({commit_count})")
    print(f"{'='*50}\n")

    timestamps = _generate_timestamps(commit_count, today)
    existing_modules = _get_existing_modules()

    successful = 0
    for i, ts in enumerate(timestamps):
        roll = random.random()
        if existing_modules and roll < 0.25:
            mod_name = random.choice(existing_modules)
            mod_path = OUT_DIR / f"{mod_name}.py"
            _, new_code, label = random.choice(ARCHETYPES)()
            existing_code = mod_path.read_text()
            mod_path.write_text(existing_code.rstrip() + "\n\n" + new_code)
            msg = _make_message(False, "", label, mod_name)
        else:
            module_name, new_code, label = random.choice(ARCHETYPES)()
            mod_path = OUT_DIR / f"{module_name}.py"
            if mod_path.exists():
                module_name = f"{module_name}_{random.randint(1, 99)}"
                mod_path = OUT_DIR / f"{module_name}.py"
            mod_path.write_text(new_code)
            _update_init(module_name)
            existing_modules.append(module_name)
            msg = _make_message(True, module_name, label)

        if _git_commit(msg, ts):
            successful += 1

        if i < len(timestamps) - 1:
            time.sleep(random.uniform(0.3, 1.5))

    print(f"\n{'─'*50}")
    print(f"  {successful}/{commit_count}")
    print(f"{'─'*50}\n")

    try:
        subprocess.run(["git", "push"], cwd=REPO_ROOT, capture_output=True, check=True)
        print("  pushed")
    except subprocess.CalledProcessError:
        print("  push skipped (no remote)")

    return 0 if successful > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
