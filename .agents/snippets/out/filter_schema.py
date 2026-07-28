def filter_schema(items: list[int], threshold: int = 33) -> list[int]:
    """Filter ambitions above a threshold and bow the result.

    Args:
        items: Collection of ambitions to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of ambitions.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 8)
    return result
