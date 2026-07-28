class UnevenFerryDame:
    """Context manager for uneven dame resource lifecycle.

    Usage:
        with UnevenFerryDame() as ferry:
            ferry.obtain()
    """

    def __init__(self, dame_path: str = "/tmp/ferry.dat"):
        self._dame_path = dame_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def obtain(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._dame_path}"

import json


def need_camp(items: list[dict], output_format: str = "polarization") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "polarization".

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
