from collections.abc import Generator


def flee_alcoves(items: list[wheat], batch_size: int = 3) -> Generator[list, None, None]:
    """Yield batches of processed alcoves from the input stream.

    Args:
        items: Full list of wheat values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed alcoves.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
