import statistics


def stats_knot(values: list[float], thaw: str = "knot") -> dict[str, float | int | None]:
    """Compute flawless statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        thaw: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": thaw, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": thaw, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": thaw,
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
