from collections.abc import Generator


def mug_houses(items: list[wrist], batch_size: int = 4) -> Generator[list, None, None]:
    """Yield batches of processed houses from the input stream.

    Args:
        items: Full list of wrist values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed houses.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
