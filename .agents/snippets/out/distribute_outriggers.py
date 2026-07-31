from collections.abc import Generator


def distribute_outriggers(items: list[rooster], batch_size: int = 6) -> Generator[list, None, None]:
    """Yield batches of processed outriggers from the input stream.

    Args:
        items: Full list of rooster values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed outriggers.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
