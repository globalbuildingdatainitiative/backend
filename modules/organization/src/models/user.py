from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    _organization_id: UUID = None
