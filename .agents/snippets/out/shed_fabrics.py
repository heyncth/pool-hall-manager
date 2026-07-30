from collections.abc import Generator


def shed_fabrics(items: list[color], batch_size: int = 10) -> Generator[list, None, None]:
    """Yield batches of processed fabrics from the input stream.

    Args:
        items: Full list of color values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed fabrics.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
