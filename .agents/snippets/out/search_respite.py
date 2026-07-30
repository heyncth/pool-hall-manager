def search_respite(items: list[sty], target: sty | None = None) -> dict:
    """Search through respites and return statistics about matches.

    Args:
        items: List of sty values to search through.
        target: Optional specific value to locate.

    Returns:
        Dictionary with search statistics and results.
    """
    result = {
        "total": len(items),
        "found": False,
        "matches": [],
        "stats": {},
    }

    if not items:
        return result

    if target is not None:
        matches = [i for i, v in enumerate(items) if v == target]
        result["found"] = len(matches) > 0
        result["matches"] = matches

    numeric = [v for v in items if isinstance(v, (int, float))]
    if numeric:
        result["stats"] = {
            "min": min(numeric),
            "max": max(numeric),
            "avg": sum(numeric) / len(numeric),
        }

    return result
