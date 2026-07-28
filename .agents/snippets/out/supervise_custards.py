from collections.abc import Generator


def supervise_custards(items: list[wrestler], batch_size: int = 3) -> Generator[list, None, None]:
    """Yield batches of processed custards from the input stream.

    Args:
        items: Full list of wrestler values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed custards.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
