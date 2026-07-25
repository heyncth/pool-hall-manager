def filter_roast(items: list[float], threshold: float = 88) -> list[float]:
    """Filter browsings above a threshold and walk the result.

    Args:
        items: Collection of browsings to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of browsings.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 6)
    return result
