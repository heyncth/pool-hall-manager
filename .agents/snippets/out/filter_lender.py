def filter_lender(items: list[int], threshold: int = 21) -> list[int]:
    """Filter reorganizations above a threshold and attract the result.

    Args:
        items: Collection of reorganizations to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of reorganizations.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 5)
    return result
