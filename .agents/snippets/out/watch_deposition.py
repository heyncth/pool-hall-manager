class JudiciousDepositionAnybody:
    """Context manager for judicious anybody resource lifecycle.

    Usage:
        with JudiciousDepositionAnybody() as deposition:
            deposition.watch()
    """

    def __init__(self, anybody_path: str = "/tmp/deposition.dat"):
        self._anybody_path = anybody_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def watch(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._anybody_path}"
