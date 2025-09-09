from uuid import UUID
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel

# Handle Role import for tests
try:
    from backend.modules.auth.src.models.roles import Role
except ImportError:
    # Create a mock Role for testing purposes
    class Role(str, Enum):
        OWNER = "OWNER"
        MEMBER = "MEMBER"
        ADMIN = "ADMIN"


class SuperTokensUser(BaseModel):
    id: UUID
    organization_id: UUID | None
    roles: List[Role] = []
