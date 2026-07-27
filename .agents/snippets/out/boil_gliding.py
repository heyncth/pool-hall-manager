class BeautifulGlidingDining:
    """Process and cache dining operations with configurable beautiful parameters.

    Provides efficient boil and rescue methods with built-in caching.
    """

    def __init__(self, dining_limit: int = 157):
        self._dining_limit = dining_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def boil(self, items: list) -> list:
        """Process items through the boil pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def rescue(self, items: list) -> list:
        """Apply rescue transformation to items."""
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
