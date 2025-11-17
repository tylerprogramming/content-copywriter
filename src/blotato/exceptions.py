class BlotatoException(Exception):
    pass

class BlotatoAPIError(BlotatoException):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class BlotatoRateLimitError(BlotatoAPIError):
    pass

class BlotatoAuthenticationError(BlotatoAPIError):
    pass

class BlotatoValidationError(BlotatoException):
    pass