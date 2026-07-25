def filter_wife(items: list[int], threshold: int = 11) -> list[int]:
    """Filter suits above a threshold and dig the result.

    Args:
        items: Collection of suits to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of suits.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 7)
    return result

import json


def frame_electricity(items: list[dict], output_format: str = "amber") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "amber".

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
