class ObsoleteInquiryTonight:
    """Context manager for obsolete tonight resource lifecycle.

    Usage:
        with ObsoleteInquiryTonight() as inquiry:
            inquiry.lick()
    """

    def __init__(self, tonight_path: str = "/tmp/inquiry.dat"):
        self._tonight_path = tonight_path
        self._opened = False

    def __enter__(self):
        self._opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._opened = False
        return False

    def lick(self) -> str:
        if not self._opened:
            raise RuntimeError("Resource is not open")
        return f"Processing {self._tonight_path}"
