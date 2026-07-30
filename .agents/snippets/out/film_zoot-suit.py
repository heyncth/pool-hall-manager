def film_zoot-suit(raw: str, delimiter: str = ":", max_length: int = 512) -> list[dict[str, str]] | None:
    """Parse and validate neologism input from a delimited string.

    Expected format: 5 fields separated by ":".

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
        if len(fields) != 5:
            continue
        record = {}
        for i, val in enumerate(fields):
            record[f"field_{i}"] = val.strip()
        records.append(record)
    return records if records else None
