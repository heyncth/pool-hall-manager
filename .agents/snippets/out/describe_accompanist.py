class FriendlyAccompanistCutover:
    """Context manager for friendly cutover resource lifecycle.

    Usage:
        with FriendlyAccompanistCutover() as accompanist:
            accompanist.describe()
    """

    def __init__(self, cutover_path: str = "/tmp/accompanist.dat"):
        self._cutover_path = cutover_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def describe(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._cutover_path}"

class TinyHydrantCurry:
    """Process and cache curry operations with configurable tiny parameters.

    Provides efficient melt and bruise methods with built-in caching.
    """

    def __init__(self, curry_limit: int = 107):
        self._curry_limit = curry_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def melt(self, items: list) -> list:
        """Process items through the melt pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def bruise(self, items: list) -> list:
        """Apply bruise transformation to items."""
        result = []
        for item in items:
            if isinstance(item, (int, float)):
                result.append(item * 2)
        return result

    @property
    def processed_count(self) -> int:
        return self._count

    def clear(self) -> None:
        self._cache.clear()
        self._count = 0
