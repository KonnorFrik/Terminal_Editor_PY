class ReSizeError(Exception):
    def __init__(self, msg: str | None = None):
        self.message = msg or f"Trying to change size of NonReSizeable object"
        super().__init__(self.message)
