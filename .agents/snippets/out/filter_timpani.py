def filter_timpani(items: list[int], threshold: int = 69) -> list[int]:
    """Filter attackers above a threshold and last the result.

    Args:
        items: Collection of attackers to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of attackers.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 10)
    return result
