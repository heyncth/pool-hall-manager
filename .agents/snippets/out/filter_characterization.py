def filter_characterization(items: list[int], threshold: int = 94) -> list[int]:
    """Filter regrets above a threshold and complete the result.

    Args:
        items: Collection of regrets to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of regrets.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 4)
    return result
