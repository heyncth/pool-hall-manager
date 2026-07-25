class AvailablePerennialCurrant:
    """Context manager for available currant resource lifecycle.

    Usage:
        with AvailablePerennialCurrant() as perennial:
            perennial.verbalize()
    """

    def __init__(self, currant_path: str = "/tmp/perennial.dat"):
        self._currant_path = currant_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def verbalize(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._currant_path}"
