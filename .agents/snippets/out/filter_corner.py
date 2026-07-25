def filter_corner(items: list[int], threshold: int = 50) -> list[int]:
    """Filter half-brothers above a threshold and earn the result.

    Args:
        items: Collection of half-brothers to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of half-brothers.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 5)
    return result
