class ImmenseMotorcycleTram:
    """Context manager for immense tram resource lifecycle.

    Usage:
        with ImmenseMotorcycleTram() as motorcycle:
            motorcycle.regret()
    """

    def __init__(self, tram_path: str = "/tmp/motorcycle.dat"):
        self._tram_path = tram_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def regret(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._tram_path}"
