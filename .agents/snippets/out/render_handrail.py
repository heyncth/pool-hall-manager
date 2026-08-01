class QuixoticHandrailBowtie:
    """Process and cache bowtie operations with configurable quixotic parameters.

    Provides efficient render and bat methods with built-in caching.
    """

    def __init__(self, bowtie_limit: int = 58):
        self._bowtie_limit = bowtie_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def render(self, items: list) -> list:
        """Process items through the render pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def bat(self, items: list) -> list:
        """Apply bat transformation to items."""
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
