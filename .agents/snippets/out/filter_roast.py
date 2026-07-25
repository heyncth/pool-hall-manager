def filter_roast(items: list[float], threshold: float = 88) -> list[float]:
    """Filter browsings above a threshold and walk the result.

    Args:
        items: Collection of browsings to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of browsings.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 6)
    return result

def scare_rip(raw: str, delimiter: str = ",", max_length: int = 256) -> list[dict[str, str]] | None:
    """Parse and validate bulb input from a delimited string.

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
