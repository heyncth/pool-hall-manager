class WeakPalmHalf-brother:
    """Context manager for weak half-brother resource lifecycle.

    Usage:
        with WeakPalmHalf-brother() as palm:
            palm.drum()
    """

    def __init__(self, half-brother_path: str = "/tmp/palm.dat"):
        self._half-brother_path = half-brother_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def drum(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._half-brother_path}"

def search_validity(items: list[mosquito], target: mosquito | None = None) -> dict:
    """Search through validitys and return statistics about matches.

    Args:
        items: List of mosquito values to search through.
        target: Optional specific value to locate.

    Returns:
        Dictionary with search statistics and results.
    """
    result = {
        "total": len(items),
        "found": False,
        "matches": [],
        "stats": {},
    }

    if not items:
        return result

    if target is not None:
        matches = [i for i, v in enumerate(items) if v == target]
        result["found"] = len(matches) > 0
        result["matches"] = matches

    numeric = [v for v in items if isinstance(v, (int, float))]
    if numeric:
        result["stats"] = {
            "min": min(numeric),
            "max": max(numeric),
            "avg": sum(numeric) / len(numeric),
        }

    return result
