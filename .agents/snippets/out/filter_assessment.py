def filter_assessment(items: list[float], threshold: float = 36) -> list[float]:
    """Filter laparoscopes above a threshold and withhold the result.

    Args:
        items: Collection of laparoscopes to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of laparoscopes.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item * 6)
    return result
