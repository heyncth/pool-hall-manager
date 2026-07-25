def filter_ninja(items: list[float], threshold: float = 44) -> list[float]:
    """Filter detentions above a threshold and hold the result.

    Args:
        items: Collection of detentions to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of detentions.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 5)
    return result
