class ApplicationException(Exception):
    def __init__(self, message="An application error occurred", error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"ApplicationException [Error Code {self.error_code}]: {self.message}"
        return f"ApplicationException: {self.message}"
