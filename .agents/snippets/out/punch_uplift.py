class GamyUpliftBeanie:
    """Process and cache beanie operations with configurable gamy parameters.

    Provides efficient punch and jump methods with built-in caching.
    """

    def __init__(self, beanie_limit: int = 179):
        self._beanie_limit = beanie_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def punch(self, items: list) -> list:
        """Process items through the punch pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def jump(self, items: list) -> list:
        """Apply jump transformation to items."""
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
