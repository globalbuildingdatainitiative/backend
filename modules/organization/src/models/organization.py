from uuid import UUID, uuid4
from typing import List, Optional

import strawberry
from beanie import Document
from pydantic import BaseModel, Field

from .country_codes import CountryCodes
from .stakeholder import StakeholderEnum
from .sort_filter import BaseFilter, FilterOptions


@strawberry.type
class OrganizationMetaData:
    stakeholders: List[StakeholderEnum] = strawberry.field(default_factory=list)


class OrganizationMetaDataModel(BaseModel):
    stakeholders: List[StakeholderEnum] = Field(default_factory=list)


class OrganizationBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    meta_data: OrganizationMetaDataModel = Field(default_factory=OrganizationMetaDataModel)


class DBOrganization(OrganizationBase, Document):
    pass


@strawberry.federation.type(name="Organization", keys=["id"])
class GraphQLOrganization:
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    meta_data: OrganizationMetaData

    @classmethod
    async def resolve_reference(cls, id: UUID) -> "GraphQLOrganization":
        from logic import get_organizations

        return (await get_organizations(filters=OrganizationFilter(id=FilterOptions(equal=id))))[0]


@strawberry.input
class InputOrganizationMetaData:
    stakeholders: List[StakeholderEnum] = strawberry.field(default_factory=list)


@strawberry.input
class InputOrganization:
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    meta_data: InputOrganizationMetaData = strawberry.field(default_factory=InputOrganizationMetaData)


@strawberry.input
class OrganizationMetaDataFilter:
    stakeholders: Optional[FilterOptions] = None


@strawberry.input
class OrganizationFilter(BaseFilter):
    id: FilterOptions | None = None
    name: FilterOptions | None = None
    address: FilterOptions | None = None
    city: FilterOptions | None = None
    country: FilterOptions | None = None
    meta_data: Optional[OrganizationMetaDataFilter] = None
