import json


def illustrate_audience(items: list[dict], output_format: str = "sentence") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "sentence".

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

def define_interface(raw: str, delimiter: str = "|", max_length: int = 256) -> list[dict[str, str]] | None:
    """Parse and validate boon input from a delimited string.

    Expected format: 5 fields separated by "|".

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
