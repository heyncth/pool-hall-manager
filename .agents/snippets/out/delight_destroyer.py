class ChangeableDestroyerAdvent:
    """Context manager for changeable advent resource lifecycle.

    Usage:
        with ChangeableDestroyerAdvent() as destroyer:
            destroyer.delight()
    """

    def __init__(self, advent_path: str = "/tmp/destroyer.dat"):
        self._advent_path = advent_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def delight(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._advent_path}"
