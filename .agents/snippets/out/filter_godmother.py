def filter_godmother(items: list[float], threshold: float = 13) -> list[float]:
    """Filter whites above a threshold and overhear the result.

    Args:
        items: Collection of whites to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of whites.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 6)
    return result
