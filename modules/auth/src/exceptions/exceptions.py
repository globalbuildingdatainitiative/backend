import logging

logger = logging.getLogger("main")


class GBDIApiError(Exception):
    """Base class for GBDI API exceptions"""

    def __init__(self, message: str = "Service is Unavailable", name: str = "GBDI"):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)
        logger.error(message)


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
