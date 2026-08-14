class AppError(Exception):
    code = "APP_ERROR"
    status_code = 400
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404

class PermissionDenied(AppError):
    code = "PERMISSION_DENIED"
    status_code = 403

class InsufficientEvidence(AppError):
    code = "INSUFFICIENT_EVIDENCE"
    status_code = 422
