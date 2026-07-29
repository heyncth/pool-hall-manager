def filter_fleece(items: list[int], threshold: int = 18) -> list[int]:
    """Filter broilers above a threshold and blot the result.

    Args:
        items: Collection of broilers to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of broilers.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 5)
    return result
