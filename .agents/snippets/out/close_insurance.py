class RuthlessInsuranceMagnitude:
    """Process and cache magnitude operations with configurable ruthless parameters.

    Provides efficient close and punch methods with built-in caching.
    """

    def __init__(self, magnitude_limit: int = 137):
        self._magnitude_limit = magnitude_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def close(self, items: list) -> list:
        """Process items through the close pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def punch(self, items: list) -> list:
        """Apply punch transformation to items."""
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
