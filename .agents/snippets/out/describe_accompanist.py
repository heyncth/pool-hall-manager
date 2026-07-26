class FriendlyAccompanistCutover:
    """Context manager for friendly cutover resource lifecycle.

    Usage:
        with FriendlyAccompanistCutover() as accompanist:
            accompanist.describe()
    """

    def __init__(self, cutover_path: str = "/tmp/accompanist.dat"):
        self._cutover_path = cutover_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def describe(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._cutover_path}"
