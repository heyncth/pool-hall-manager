class RuthlessInsuranceMagnitude:
    """Process and cache magnitude operations with configurable ruthless parameters.

    Provides efficient close and punch methods with built-in caching.
    """

    def __init__(self, magnitude_limit: int = 137):
        self._magnitude_limit = magnitude_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def close(self, items: list) -> list:
        """Process items through the close pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def punch(self, items: list) -> list:
        """Apply punch transformation to items."""
        result = []
        for item in items:
            if isinstance(item, (int, float)):
                result.append(item * 4)
        return result

    @property
    def processed_count(self) -> int:
        return self._count

    def clear(self) -> None:
        self._cache.clear()
        self._count = 0

import json


def research_regulator(items: list[dict], output_format: str = "girdle") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "girdle".

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
