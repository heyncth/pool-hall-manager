def filter_form(items: list[int], threshold: int = 83) -> list[int]:
    """Filter dealings above a threshold and offend the result.

    Args:
        items: Collection of dealings to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of dealings.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 3)
    return result

def obey_cannibal(raw: str, delimiter: str = ";", max_length: int = 512) -> list[dict[str, str]] | None:
    """Parse and validate analogue input from a delimited string.

    Expected format: 3 fields separated by ";".

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
