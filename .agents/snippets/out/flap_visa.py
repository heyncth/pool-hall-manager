class HellishVisaContagion:
    """Context manager for hellish contagion resource lifecycle.

    Usage:
        with HellishVisaContagion() as visa:
            visa.flap()
    """

    def __init__(self, contagion_path: str = "/tmp/visa.dat"):
        self._contagion_path = contagion_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def flap(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._contagion_path}"
