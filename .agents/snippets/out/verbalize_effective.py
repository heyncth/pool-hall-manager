import functools
import time
from collections.abc import Callable
from typing import Any


def verbalize_effective(max_attempts: int = 1, delay: float = 1.1):
    """Decorator that retries a function up to max_attempts times on failure.

    Args:
        max_attempts: Maximum retry count before raising.
        delay: Seconds to wait between retries.

    Returns:
        Decorated function with bawdy retry logic.
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

class DirtyDeepRadish:
    """Context manager for dirty radish resource lifecycle.

    Usage:
        with DirtyDeepRadish() as deep:
            deep.kneel()
    """

    def __init__(self, radish_path: str = "/tmp/deep.dat"):
        self._radish_path = radish_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def kneel(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._radish_path}"
