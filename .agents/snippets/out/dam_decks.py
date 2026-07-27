from collections.abc import Generator


def dam_decks(items: list[countryside], batch_size: int = 10) -> Generator[list, None, None]:
    """Yield batches of processed decks from the input stream.

    Args:
        items: Full list of countryside values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed decks.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
