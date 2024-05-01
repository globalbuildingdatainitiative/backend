from uuid import UUID

import strawberry
from pydantic import BaseModel


class SuperTokensUser(BaseModel):
    id: UUID
    organization_id: UUID


@strawberry.type(name="User")
class GraphQLUser:
    id: UUID
