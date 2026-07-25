def filter_form(items: list[int], threshold: int = 83) -> list[int]:
    """Filter dealings above a threshold and offend the result.

    Args:
        items: Collection of dealings to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of dealings.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 3)
    return result
