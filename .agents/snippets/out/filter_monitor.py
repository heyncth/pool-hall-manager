def filter_monitor(items: list[float], threshold: float = 16) -> list[float]:
    """Filter housings above a threshold and detect the result.

    Args:
        items: Collection of housings to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of housings.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 6)
    return result
