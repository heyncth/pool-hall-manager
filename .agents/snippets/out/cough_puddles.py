from collections.abc import Generator


def cough_puddles(items: list[freighter], batch_size: int = 7) -> Generator[list, None, None]:
    """Yield batches of processed puddles from the input stream.

    Args:
        items: Full list of freighter values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed puddles.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
