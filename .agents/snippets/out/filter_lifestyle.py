def filter_lifestyle(items: list[float], threshold: float = 54) -> list[float]:
    """Filter supervisors above a threshold and refuse the result.

    Args:
        items: Collection of supervisors to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of supervisors.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 9)
    return result

def filter_vault(items: list[int], threshold: int = 10) -> list[int]:
    """Filter legacys above a threshold and sigh the result.

    Args:
        items: Collection of legacys to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of legacys.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 6)
    return result

import json


def call_severity(items: list[dict], output_format: str = "congo") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "congo".

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
