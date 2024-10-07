from uuid import UUID, uuid4
from typing import List

import strawberry
from beanie import Document
from pydantic import BaseModel, Field

from .country_codes import CountryCodes
from .sort_filter import BaseFilter, FilterOptions


class OrganizationBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    stakeholders: List[str] = Field(default_factory=list)


class DBOrganization(OrganizationBase, Document):
    pass


@strawberry.federation.type(name="Organization", keys=["id"])
class GraphQLOrganization:
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    stakeholders: List[str] = Field(default_factory=list)

    @classmethod
    async def resolve_reference(cls, id: UUID) -> "GraphQLOrganization":
        from logic import get_organizations

        return (await get_organizations(filters=OrganizationFilter(id=FilterOptions(equal=id))))[0]


@strawberry.input
class InputOrganization:
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    stakeholders: List[str] = Field(default_factory=list)


@strawberry.input
class OrganizationFilter(BaseFilter):
    id: FilterOptions | None = None
    name: FilterOptions | None = None
    address: FilterOptions | None = None
    city: FilterOptions | None = None
    country: FilterOptions | None = None
    stakeholders: FilterOptions | None = None
