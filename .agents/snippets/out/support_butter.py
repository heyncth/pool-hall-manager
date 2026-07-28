import json


def support_butter(items: list[dict], output_format: str = "admission") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "admission".

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

def filter_node(items: list[int], threshold: int = 20) -> list[int]:
    """Filter plays above a threshold and slip the result.

    Args:
        items: Collection of plays to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of plays.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 6)
    return result
