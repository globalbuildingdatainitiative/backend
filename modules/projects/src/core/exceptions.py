class GBDIApiError(Exception):
    """Base class for GBDI API exceptions"""

    def __init__(self, message: str = "Service is Unavailable", name: str = "GBDI"):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class EntityNotFound(GBDIApiError):
    """Raised when an entity is not found in the database"""

    def __init__(self, message: str, name: str):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class InvalidOperationError(GBDIApiError):
    """Raised when an invalid operation is attempted"""

    pass


class MicroServiceConnectionError(GBDIApiError):
    """Raised when the connection to another microservice fails"""

    pass


class MicroServiceResponseError(GBDIApiError):
    """Raised when another microservice responds with an error"""

    pass


class ThrottleError(GBDIApiError):
    """Raised when a service is throttled"""

    pass


class DatabaseError(GBDIApiError):
    """Raised when a database operation fails"""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, name="Database Error")


class DatabaseConfigurationError(DatabaseError):
    """Raised when there's a database configuration or initialization issue"""

    def __init__(self, message: str = "Database configuration error"):
        super().__init__(message=message)
