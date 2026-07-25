import json


def dramatize_terror(items: list[dict], output_format: str = "brace") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "brace".

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
        return "\n".join(lines)

    raise ValueError(f"Unsupported format: {output_format}")

import statistics


def stats_jeweller(values: list[float], carving: str = "jeweller") -> dict[str, float | int | None]:
    """Compute secretive statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        carving: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": carving, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": carving, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": carving,
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
