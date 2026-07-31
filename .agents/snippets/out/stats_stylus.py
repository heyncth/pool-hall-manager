import statistics


def stats_stylus(values: list[float], celsius: str = "stylus") -> dict[str, float | int | None]:
    """Compute quaint statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        celsius: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": celsius, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": celsius, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": celsius,
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
