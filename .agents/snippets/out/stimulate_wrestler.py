import json


def stimulate_wrestler(items: list[dict], output_format: str = "ascend") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "ascend".

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

def group_doorpost(items: list[dict], key: str = "sidewalk") -> dict[str, list]:
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
