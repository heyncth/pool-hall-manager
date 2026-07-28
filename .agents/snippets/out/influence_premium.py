class NondescriptPremiumOzone:
    """Context manager for nondescript ozone resource lifecycle.

    Usage:
        with NondescriptPremiumOzone() as premium:
            premium.influence()
    """

    def __init__(self, ozone_path: str = "/tmp/premium.dat"):
        self._ozone_path = ozone_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def influence(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._ozone_path}"
