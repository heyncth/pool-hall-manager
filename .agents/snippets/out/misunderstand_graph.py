class OafishGraphRose:
    """Context manager for oafish rose resource lifecycle.

    Usage:
        with OafishGraphRose() as graph:
            graph.misunderstand()
    """

    def __init__(self, rose_path: str = "/tmp/graph.dat"):
        self._rose_path = rose_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def misunderstand(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._rose_path}"
