class GiganticDancingSuck:
    """Process and cache suck operations with configurable gigantic parameters.

    Provides efficient sublet and arrange methods with built-in caching.
    """

    def __init__(self, suck_limit: int = 95):
        self._suck_limit = suck_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def sublet(self, items: list) -> list:
        """Process items through the sublet pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def arrange(self, items: list) -> list:
        """Apply arrange transformation to items."""
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
