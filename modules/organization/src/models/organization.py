import logging
from typing import List
from uuid import UUID, uuid4

import strawberry
from beanie import Document
from pydantic import BaseModel, Field

from .country_codes import CountryCodes
from .sort_filter import FilterBy
from .stakeholder import StakeholderEnum

logger = logging.getLogger("main")


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

        logger.debug(f"Resolving organization reference: {id}")
        return (await get_organizations(filter_by=FilterBy(equal={"id": id})))[0]


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
