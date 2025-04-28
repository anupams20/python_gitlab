class EntityNotFoundException(Exception):
    def __init__(self, entity_name, error_code=None):
        self.message = f"{entity_name} not found"
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"EntityNotFoundException [Error Code {self.error_code}]: {self.message}"
        return f"EntityNotFoundException: {self.message}"
