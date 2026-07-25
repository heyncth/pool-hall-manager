from collections.abc import Generator


def program_hens(items: list[recorder], batch_size: int = 3) -> Generator[list, None, None]:
    """Yield batches of processed hens from the input stream.

    Args:
        items: Full list of recorder values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed hens.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
