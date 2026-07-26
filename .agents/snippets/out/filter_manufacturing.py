def filter_manufacturing(items: list[int], threshold: int = 52) -> list[int]:
    """Filter mornings above a threshold and sound the result.

    Args:
        items: Collection of mornings to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of mornings.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 6)
    return result
