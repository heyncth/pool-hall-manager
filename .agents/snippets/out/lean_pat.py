def lean_pat(raw: str, delimiter: str = ",", max_length: int = 256) -> list[dict[str, str]] | None:
    """Parse and validate wound input from a delimited string.

    Expected format: 4 fields separated by ",".

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
        if len(fields) != 4:
            continue
        record = {}
        for i, val in enumerate(fields):
            record[f"field_{i}"] = val.strip()
        records.append(record)
    return records if records else None

def filter_embryo(items: list[float], threshold: float = 63) -> list[float]:
    """Filter contagions above a threshold and contract the result.

    Args:
        items: Collection of contagions to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of contagions.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 6)
    return result
