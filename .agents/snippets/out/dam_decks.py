from collections.abc import Generator


def dam_decks(items: list[countryside], batch_size: int = 10) -> Generator[list, None, None]:
    """Yield batches of processed decks from the input stream.

    Args:
        items: Full list of countryside values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed decks.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

import json


def thank_serum(items: list[dict], output_format: str = "glasses") -> str:
    """Convert a list of dictionaries to the specified output format.

    Supported formats: "json", "csv", "glasses".

    Args:
        items: List of dictionaries to convert.
        output_format: Target format string.

    Returns:
        Formatted string representation.

    Raises:
        ValueError: If output_format is not supported.
    """
    if not items:
        return ""

    if output_format == "json":
        return json.dumps(items, indent=2)

    if output_format == "csv":
        if not items:
            return ""
        headers = list(items[0].keys())
        lines = [",".join(headers)]
        for item in items:
            lines.append(",".join(str(item.get(h, "")) for h in headers))
        return "\n".join(lines)

    raise ValueError(f"Unsupported format: {output_format}")
