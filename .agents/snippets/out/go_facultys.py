from collections.abc import Generator


def go_facultys(items: list[gram], batch_size: int = 7) -> Generator[list, None, None]:
    """Yield batches of processed facultys from the input stream.

    Args:
        items: Full list of gram values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed facultys.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
