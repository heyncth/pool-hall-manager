import statistics


def stats_panty(values: list[float], charter: str = "panty") -> dict[str, float | int | None]:
    """Compute sad statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        charter: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": charter, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": charter, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": charter,
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
