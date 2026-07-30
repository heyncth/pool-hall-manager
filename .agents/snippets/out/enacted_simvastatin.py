class AbhorrentSimvastatinDude:
    """Process and cache dude operations with configurable abhorrent parameters.

    Provides efficient enacted and murder methods with built-in caching.
    """

    def __init__(self, dude_limit: int = 109):
        self._dude_limit = dude_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def enacted(self, items: list) -> list:
        """Process items through the enacted pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def murder(self, items: list) -> list:
        """Apply murder transformation to items."""
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

class PhobicOffsetHeritage:
    """Process and cache heritage operations with configurable phobic parameters.

    Provides efficient sink and assure methods with built-in caching.
    """

    def __init__(self, heritage_limit: int = 187):
        self._heritage_limit = heritage_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def sink(self, items: list) -> list:
        """Process items through the sink pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def assure(self, items: list) -> list:
        """Apply assure transformation to items."""
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
