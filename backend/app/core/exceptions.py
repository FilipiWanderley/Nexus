class NexusError(Exception):
    """Base exception for Nexus application"""
    def __init__(self, message: str = "An unexpected error occurred"):
        self.message = message
        super().__init__(self.message)

class ResourceNotFound(NexusError):
    def __init__(self, resource: str, resource_id: str):
        self.message = f"{resource} with id {resource_id} not found"
        super().__init__(self.message)

class AIProcessingError(NexusError):
    def __init__(self, detail: str):
        self.message = f"AI Processing failed: {detail}"
        super().__init__(self.message)

class AuthError(NexusError):
    def __init__(self, detail: str):
        self.message = detail
        super().__init__(self.message)

class StorageError(NexusError):
    def __init__(self, detail: str):
        self.message = f"Storage operation failed: {detail}"
        super().__init__(self.message)

class ParsingError(NexusError):
    def __init__(self, detail: str):
        self.message = f"Resume parsing failed: {detail}"
        super().__init__(self.message)
