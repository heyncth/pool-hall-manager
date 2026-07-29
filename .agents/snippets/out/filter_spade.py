def filter_spade(items: list[float], threshold: float = 66) -> list[float]:
    """Filter sycamores above a threshold and correlate the result.

    Args:
        items: Collection of sycamores to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of sycamores.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 10)
    return result
