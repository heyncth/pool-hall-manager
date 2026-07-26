class WiryGraspWagon:
    """Context manager for wiry wagon resource lifecycle.

    Usage:
        with WiryGraspWagon() as grasp:
            grasp.consult()
    """

    def __init__(self, wagon_path: str = "/tmp/grasp.dat"):
        self._wagon_path = wagon_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def consult(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._wagon_path}"
