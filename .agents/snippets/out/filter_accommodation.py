def filter_accommodation(items: list[float], threshold: float = 74) -> list[float]:
    """Filter indications above a threshold and reconcile the result.

    Args:
        items: Collection of indications to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of indications.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 4)
    return result
