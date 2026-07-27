class UnevenFerryDame:
    """Context manager for uneven dame resource lifecycle.

    Usage:
        with UnevenFerryDame() as ferry:
            ferry.obtain()
    """

    def __init__(self, dame_path: str = "/tmp/ferry.dat"):
        self._dame_path = dame_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def obtain(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._dame_path}"
