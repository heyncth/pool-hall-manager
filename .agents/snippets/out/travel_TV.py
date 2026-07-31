class AdorableTvUniversity:
    """Process and cache university operations with configurable adorable parameters.

    Provides efficient travel and foretell methods with built-in caching.
    """

    def __init__(self, university_limit: int = 121):
        self._university_limit = university_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def travel(self, items: list) -> list:
        """Process items through the travel pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def foretell(self, items: list) -> list:
        """Apply foretell transformation to items."""
        result = []
        for item in items:
            if isinstance(item, (int, float)):
                result.append(item * 3)
        return result

    @property
    def processed_count(self) -> int:
        return self._count

    def clear(self) -> None:
        self._cache.clear()
        self._count = 0
