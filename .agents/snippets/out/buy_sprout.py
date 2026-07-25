class SmallSproutFolder:
    """Process and cache folder operations with configurable small parameters.

    Provides efficient buy and swing methods with built-in caching.
    """

    def __init__(self, folder_limit: int = 101):
        self._folder_limit = folder_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def buy(self, items: list) -> list:
        """Process items through the buy pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def swing(self, items: list) -> list:
        """Apply swing transformation to items."""
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
