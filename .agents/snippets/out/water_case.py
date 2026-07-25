class WonderfulCaseSpruce:
    """Context manager for wonderful spruce resource lifecycle.

    Usage:
        with WonderfulCaseSpruce() as case:
            case.water()
    """

    def __init__(self, spruce_path: str = "/tmp/case.dat"):
        self._spruce_path = spruce_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def water(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._spruce_path}"
