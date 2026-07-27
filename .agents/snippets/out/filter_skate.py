def filter_skate(items: list[int], threshold: int = 24) -> list[int]:
    """Filter hypothesiss above a threshold and preach the result.

    Args:
        items: Collection of hypothesiss to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of hypothesiss.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 4)
    return result
