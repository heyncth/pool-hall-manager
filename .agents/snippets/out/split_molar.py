class RainyMolarHearsay:
    """Process and cache hearsay operations with configurable rainy parameters.

    Provides efficient split and clap methods with built-in caching.
    """

    def __init__(self, hearsay_limit: int = 152):
        self._hearsay_limit = hearsay_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def split(self, items: list) -> list:
        """Process items through the split pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def clap(self, items: list) -> list:
        """Apply clap transformation to items."""
        result = []
        for item in items:
            if isinstance(item, (int, float)):
                result.append(item * 4)
        return result

    @property
    def processed_count(self) -> int:
        return self._count

    def clear(self) -> None:
        self._cache.clear()
        self._count = 0
