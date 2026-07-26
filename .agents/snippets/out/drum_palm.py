class WeakPalmHalf-brother:
    """Context manager for weak half-brother resource lifecycle.

    Usage:
        with WeakPalmHalf-brother() as palm:
            palm.drum()
    """

    def __init__(self, half-brother_path: str = "/tmp/palm.dat"):
        self._half-brother_path = half-brother_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def drum(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._half-brother_path}"
