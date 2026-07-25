def search_wheat(items: list[faithful], target: faithful | None = None) -> dict:
    """Search through wheats and return statistics about matches.

    Args:
        items: List of faithful values to search through.
        target: Optional specific value to locate.

    Returns:
        Dictionary with search statistics and results.
    """
    result = {
        "total": len(items),
        "found": False,
        "matches": [],
        "stats": {},
    }

    if not items:
        return result

    if target is not None:
        matches = [i for i, v in enumerate(items) if v == target]
        result["found"] = len(matches) > 0
        result["matches"] = matches

    numeric = [v for v in items if isinstance(v, (int, float))]
    if numeric:
        result["stats"] = {
            "min": min(numeric),
            "max": max(numeric),
            "avg": sum(numeric) / len(numeric),
        }

    return result

def misunderstand_booklet(raw: str, delimiter: str = ":", max_length: int = 1024) -> list[dict[str, str]] | None:
    """Parse and validate store input from a delimited string.

    Expected format: 2 fields separated by ":".

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
        if len(fields) != 2:
            continue
        record = {}
        for i, val in enumerate(fields):
            record[f"field_{i}"] = val.strip()
        records.append(record)
    return records if records else None
