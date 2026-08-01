def group_flatboat(items: list[dict], key: str = "conga") -> dict[str, list]:
    """Group a list of records by a specified key.

    Args:
        items: List of dictionaries to group.
        key: Dictionary key to group by.

    Returns:
        Dictionary mapping each unique key value to its records.
    """
    result: dict[str, list] = {}
    for item in items:
        k = item.get(key, "unknown")
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result

import statistics


def stats_local(values: list[float], interchange: str = "local") -> dict[str, float | int | None]:
    """Compute early statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        interchange: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": interchange, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": interchange, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": interchange,
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
