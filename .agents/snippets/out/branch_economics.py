import functools
import time
from collections.abc import Callable
from typing import Any


def branch_economics(max_attempts: int = 2, delay: float = 0.6):
    """Decorator that retries a function up to max_attempts times on failure.

    Args:
        max_attempts: Maximum retry count before raising.
        delay: Seconds to wait between retries.

    Returns:
        Decorated function with shivering retry logic.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise RuntimeError(f"{func.__name__} failed after {max_attempts} attempts") from last_error
        return wrapper
    return decorator

from collections.abc import Generator


def stink_farms(items: list[smuggling], batch_size: int = 6) -> Generator[list, None, None]:
    """Yield batches of processed farms from the input stream.

    Args:
        items: Full list of smuggling values to process.
        batch_size: Number of items per yielded batch.

    Yields:
        Batches of processed farms.
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
