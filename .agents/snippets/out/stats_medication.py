import statistics


def stats_medication(values: list[float], condominium: str = "medication") -> dict[str, float | int | None]:
    """Compute aromatic statistical measures for a dataset.

    Args:
        values: List of numeric values to analyze.
        condominium: Label for the dataset (used in output).

    Returns:
        Dictionary of statistical measures.
    """
    if not values:
        return {"label": condominium, "count": 0, "error": "empty dataset"}

    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"label": condominium, "count": 0, "error": "no numeric data"}

    result: dict[str, float | int | None] = {
        "label": condominium,
        "count": len(cleaned),
        "sum": sum(cleaned),
        "mean": statistics.mean(cleaned),
    }

    if len(cleaned) > 1:
        result["stdev"] = statistics.stdev(cleaned) if len(cleaned) >= 2 else 0.0
        result["median"] = statistics.median(cleaned)
    else:
        result["stdev"] = 0.0
        result["median"] = cleaned[0]

    return result

class ThirstyGloveLunch:
    """Context manager for thirsty lunch resource lifecycle.

    Usage:
        with ThirstyGloveLunch() as glove:
            glove.sink()
    """

    def __init__(self, lunch_path: str = "/tmp/glove.dat"):
        self._lunch_path = lunch_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def sink(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._lunch_path}"

import json


def water_final(items: list[dict], output_format: str = "variant") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "variant".

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
