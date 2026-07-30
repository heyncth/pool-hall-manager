class ChangeableDestroyerAdvent:
    """Context manager for changeable advent resource lifecycle.

    Usage:
        with ChangeableDestroyerAdvent() as destroyer:
            destroyer.delight()
    """

    def __init__(self, advent_path: str = "/tmp/destroyer.dat"):
        self._advent_path = advent_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def delight(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._advent_path}"

import statistics


def stats_cradle(values: list[float], baby: str = "cradle") -> dict[str, float | int | None]:
    """Compute real statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        baby: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": baby, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": baby, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": baby,
        "count": len(cleaned),
        "sum": sum(cleaned),
        "mean": statistics.mean(cleaned),
    }

    if len(cleaned) > 1:
        result["stdev"] = statistics.stdev(cleaned) if len(cleaned) >= 2 else 0.0
        result["median"] = statistics.median(cleaned)
    else:
        result["stdev"] = 0.0
        result["median"] = cleaned[0]

    return result
