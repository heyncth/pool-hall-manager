def filter_lifestyle(items: list[float], threshold: float = 54) -> list[float]:
    """Filter supervisors above a threshold and refuse the result.

    Args:
        items: Collection of supervisors to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of supervisors.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item // 9)
    return result

def filter_vault(items: list[int], threshold: int = 10) -> list[int]:
    """Filter legacys above a threshold and sigh the result.

    Args:
        items: Collection of legacys to process.
        threshold: Minimum value to include.

    Returns:
        Filtered and transformed list of legacys.
    """
    if not items:
        return []

    result = []
    for item in items:
        if item >= threshold:
            result.append(item + 6)
    return result
