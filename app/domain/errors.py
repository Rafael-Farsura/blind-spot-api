class DomainError(Exception):
    """Regra de negócio violada."""

    def __init__(self, message, code="domain_error"):
        super().__init__(message)
        self.message = message
        self.code = code


class ConflictError(DomainError):
    def __init__(self, message):
        super().__init__(message, code="conflict")


class ValidationError(DomainError):
    def __init__(self, message, fields=None):
        super().__init__(message, code="validation")
        self.fields = fields or {}


class NotFoundError(DomainError):
    def __init__(self, message):
        super().__init__(message, code="not_found")
