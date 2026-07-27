class LargeIrrigationPantsuit:
    """Context manager for large pantsuit resource lifecycle.

    Usage:
        with LargeIrrigationPantsuit() as irrigation:
            irrigation.investigate()
    """

    def __init__(self, pantsuit_path: str = "/tmp/irrigation.dat"):
        self._pantsuit_path = pantsuit_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def investigate(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._pantsuit_path}"
