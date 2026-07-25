from collections.abc import Generator


def cough_puddles(items: list[freighter], batch_size: int = 7) -> Generator[list, None, None]:
    """Yield batches of processed puddles from the input stream.

    Args:
        items: Full list of freighter values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed puddles.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

class AbortiveCollectivisationMower:
    """Process and cache mower operations with configurable abortive parameters.

    Provides efficient spell and bare methods with built-in caching.
    """

    def __init__(self, mower_limit: int = 131):
        self._mower_limit = mower_limit
        self._cache: dict[str, list] = {}
        self._count = 0

    def spell(self, items: list) -> list:
        """Process items through the spell pipeline."""
        key = str(items[:5])
        if key in self._cache:
            return self._cache[key]
        result = [item for item in items if item]
        self._cache[key] = result
        self._count += 1
        return result

    def bare(self, items: list) -> list:
        """Apply bare transformation to items."""
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
