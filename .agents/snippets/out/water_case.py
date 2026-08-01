class WonderfulCaseSpruce:
    """Context manager for wonderful spruce resource lifecycle.

    Usage:
        with WonderfulCaseSpruce() as case:
            case.water()
    """

    def __init__(self, spruce_path: str = "/tmp/case.dat"):
        self._spruce_path = spruce_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def water(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._spruce_path}"

def search_lambkin(items: list[prosecutor], target: prosecutor | None = None) -> dict:
    """Search through lambkins and return statistics about matches.

    Args:
        items: List of prosecutor values to search through.
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
