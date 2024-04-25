import datetime
from uuid import UUID, uuid4

import strawberry
from beanie import Document, Link
from pydantic import BaseModel, Field
from .sort_filter import BaseFilter, SortOptions, FilterOptions
from .project import DBProject, GraphQLProject, InputProject


class ContributionBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    uploaded_at: datetime.datetime
    user_id: UUID
    organization_id: UUID


class DBContribution(ContributionBase, Document):
    project: Link[DBProject]


@strawberry.experimental.pydantic.type(model=ContributionBase, all_fields=True, name="Contribution")
class GraphQLContribution:
    project: GraphQLProject


class InputContribution(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    uploaded_at: datetime.datetime = datetime.datetime.now()
    project: InputProject


class ContributionFilters(BaseFilter):
    id: FilterOptions | None = None
    upload_at: FilterOptions | None = None
    user_id: FilterOptions | None = None
    organization_id: FilterOptions | None = None


class ContributionSort(BaseFilter):
    id: SortOptions | None = None
    upload_at: SortOptions | None = None
    user_id: SortOptions | None = None
    organization_id: SortOptions | None = None
