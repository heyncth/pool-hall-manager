from collections.abc import Generator


def guess_empires(items: list[probe], batch_size: int = 6) -> Generator[list, None, None]:
    """Yield batches of processed empires from the input stream.

    Args:
        items: Full list of probe values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed empires.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
