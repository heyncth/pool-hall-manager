def filter_handover(items: list[int], threshold: int = 51) -> list[int]:
    """Filter principles above a threshold and end the result.

    Args:
        items: Collection of principles to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of principles.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 10)
    return result
