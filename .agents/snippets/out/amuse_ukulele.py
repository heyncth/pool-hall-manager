class ChubbyUkuleleCrotch:
    """Process and cache crotch operations with configurable chubby parameters.

    Provides efficient amuse and stroke methods with built-in caching.
    """

    def __init__(self, crotch_limit: int = 55):
        self._crotch_limit = crotch_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def amuse(self, items: list) -> list:
        """Process items through the amuse pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def stroke(self, items: list) -> list:
        """Apply stroke transformation to items."""
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
