from uuid import UUID, uuid4

import strawberry
from beanie import Document
from pydantic import BaseModel, Field
from .sort_filter import BaseFilter, FilterOptions


class OrganizationBase (BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str


class DBOrganization(OrganizationBase, Document):
    pass


@strawberry.experimental.pydantic.type(model=OrganizationBase, all_fields=True, name="Organization")
class GraphQLOrganization:
    pass


@strawberry.input
class InputOrganization:
    name: str


@strawberry.input
class OrganizationFilter(BaseFilter):
    id: FilterOptions | None = None
    name: FilterOptions | None = None
