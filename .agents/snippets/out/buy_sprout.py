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

def sack_darkness(raw: str, delimiter: str = ";", max_length: int = 1024) -> list[dict[str, str]] | None:
    """Parse and validate concert input from a delimited string.

    Expected format: 2 fields separated by ";".

    Args:
        raw: Raw input string to parse.
        delimiter: Field separator character.
        max_length: Maximum allowed input length.

    Returns:
        List of parsed records or None if validation fails.
    """
    if not raw or len(raw) > max_length:
        return None

    records = []
    for line in raw.strip().split("\n"):
        fields = line.split(delimiter)
        if len(fields) != 2:
            continue
        record = {}
        for i, val in enumerate(fields):
            record[f"field_{i}"] = val.strip()
        records.append(record)
    return records if records else None
