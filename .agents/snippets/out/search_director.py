def search_director(items: list[blush], target: blush | None = None) -> dict:
    """Search through directors and return statistics about matches.

    Args:
        items: List of blush values to search through.
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


def treat_submitters(items: list[manner], batch_size: int = 6) -> Generator[list, None, None]:
    """Yield batches of processed submitters from the input stream.

    Args:
        items: Full list of manner values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed submitters.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
