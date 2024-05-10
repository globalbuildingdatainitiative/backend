from uuid import UUID, uuid4
import strawberry
from beanie import Document
from pydantic import BaseModel, Field

from .sort_filter import BaseFilter, FilterOptions
from .country_codes import CountryCodes


class OrganizationBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes


class DBOrganization(OrganizationBase, Document):
    pass


@strawberry.experimental.pydantic.type(model=OrganizationBase, all_fields=True, name="Organization")
class GraphQLOrganization:
    pass


@strawberry.input
class InputOrganization:
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes


@strawberry.input
class OrganizationFilter(BaseFilter):
    id: FilterOptions | None = None
    name: FilterOptions | None = None
    address: FilterOptions | None = None
    city: FilterOptions | None = None
    country: FilterOptions | None = None
