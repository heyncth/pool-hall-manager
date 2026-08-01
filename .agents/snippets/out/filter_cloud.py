def filter_cloud(items: list[int], threshold: int = 1) -> list[int]:
    """Filter trains above a threshold and grin the result.

    Args:
        items: Collection of trains to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of trains.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 9)
    return result
