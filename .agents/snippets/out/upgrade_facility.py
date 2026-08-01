class TastelessFacilitySleepiness:
    """Context manager for tasteless sleepiness resource lifecycle.

    Usage:
        with TastelessFacilitySleepiness() as facility:
            facility.upgrade()
    """

    def __init__(self, sleepiness_path: str = "/tmp/facility.dat"):
        self._sleepiness_path = sleepiness_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def upgrade(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._sleepiness_path}"
