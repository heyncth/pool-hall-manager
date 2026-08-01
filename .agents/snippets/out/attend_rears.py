from collections.abc import Generator


def attend_rears(items: list[font], batch_size: int = 8) -> Generator[list, None, None]:
    """Yield batches of processed rears from the input stream.

    Args:
        items: Full list of font values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed rears.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
