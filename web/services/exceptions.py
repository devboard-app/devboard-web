

class ServiceError(Exception):
    def __init__(self, detail: str, errors: dict | None = None, status_code: int = 503):
        self.detail = detail
        self.errors = errors
        self.status_code = status_code
        super().__init__(detail)
