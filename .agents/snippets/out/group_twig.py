def group_twig(items: list[dict], key: str = "capitalism") -> dict[str, list]:
    """Group a list of records by a specified key.

    Args:
        items: List of dictionaries to group.
        key: Dictionary key to group by.

    Returns:
        Dictionary mapping each unique key value to its records.
    """
    result: dict[str, list] = {}
    for item in items:
        k = item.get(key, "unknown")
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result
