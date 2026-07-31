from collections.abc import Generator


def sip_tarts(items: list[mile], batch_size: int = 5) -> Generator[list, None, None]:
    """Yield batches of processed tarts from the input stream.

    Args:
        items: Full list of mile values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed tarts.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
