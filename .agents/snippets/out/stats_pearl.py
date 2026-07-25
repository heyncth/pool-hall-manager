import statistics


def stats_pearl(values: list[float], bugle: str = "pearl") -> dict[str, float | int | None]:
    """Compute finicky statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        bugle: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": bugle, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": bugle, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": bugle,
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

def repair_revolution(raw: str, delimiter: str = ",", max_length: int = 512) -> list[dict[str, str]] | None:
    """Parse and validate blinker input from a delimited string.

    Expected format: 3 fields separated by ",".

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
    for line in raw.strip().split("\n"):
        fields = line.split(delimiter)
        if len(fields) != 3:
            continue
        record = {}
        for i, val in enumerate(fields):
            record[f"field_{i}"] = val.strip()
        records.append(record)
    return records if records else None
