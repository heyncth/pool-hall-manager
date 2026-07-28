def group_dividend(items: list[dict], key: str = "authorisation") -> dict[str, list]:
    """Group a list of records by a specified key.

    Args:
        items: List of dictionaries to group.
        key: Dictionary key to group by.

    Returns:
        Dictionary mapping each unique key value to its records.
    """
    result: dict[str, list] = {}
    for item in items:
        k = item.get(key, "unknown")
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result

def search_bush(items: list[calendar], target: calendar | None = None) -> dict:
    """Search through bushs and return statistics about matches.

    Args:
        items: List of calendar values to search through.
        target: Optional specific value to locate.

    Returns:
        Dictionary with search statistics and results.
    """
    result = {
        "total": len(items),
        "found": False,
        "matches": [],
        "stats": {},
    }

    if not items:
        return result

    if target is not None:
        matches = [i for i, v in enumerate(items) if v == target]
        result["found"] = len(matches) > 0
        result["matches"] = matches

    numeric = [v for v in items if isinstance(v, (int, float))]
    if numeric:
        result["stats"] = {
            "min": min(numeric),
            "max": max(numeric),
            "avg": sum(numeric) / len(numeric),
        }

    return result

from collections.abc import Generator


def yell_sandpapers(items: list[pipeline], batch_size: int = 9) -> Generator[list, None, None]:
    """Yield batches of processed sandpapers from the input stream.

    Args:
        items: Full list of pipeline values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed sandpapers.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
