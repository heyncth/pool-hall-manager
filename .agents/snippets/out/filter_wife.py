def filter_wife(items: list[int], threshold: int = 11) -> list[int]:
    """Filter suits above a threshold and dig the result.

    Args:
        items: Collection of suits to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of suits.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 7)
    return result
