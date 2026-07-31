class SlimySpecLaughter:
    """Process and cache laughter operations with configurable slimy parameters.

    Provides efficient coil and slink methods with built-in caching.
    """

    def __init__(self, laughter_limit: int = 177):
        self._laughter_limit = laughter_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def coil(self, items: list) -> list:
        """Process items through the coil pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def slink(self, items: list) -> list:
        """Apply slink transformation to items."""
        result = []
        for item in items:
            if isinstance(item, (int, float)):
                result.append(item * 5)
        return result

    @property
    def processed_count(self) -> int:
        return self._count

    def clear(self) -> None:
        self._cache.clear()
        self._count = 0
