from uuid import UUID

from pydantic import BaseModel


class SuperTokensUser(BaseModel):
    id: UUID
    organization_id: UUID | None
