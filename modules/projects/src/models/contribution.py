import datetime
from uuid import UUID, uuid4
import strawberry
from beanie import Document, Link
from pydantic import BaseModel, Field

from .project import DBProject, GraphQLProject, GraphQLInputProject
from .sort_filter import BaseFilter, FilterBy


class ContributionBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.now, alias="uploadedAt")
    user_id: UUID = Field(alias="userId")
    organization_id: UUID = Field(alias="organizationId")


class DBContribution(ContributionBase, Document):
    project: Link[DBProject]


async def get_user_info(root: "GraphQLContribution") -> "GraphQLUser":
    return GraphQLUser(id=root.user_id)


@strawberry.federation.type(name="User", keys=["id"])
class GraphQLUser:
    id: UUID


@strawberry.experimental.pydantic.type(model=ContributionBase, all_fields=True, name="Contribution")
class GraphQLContribution:
    project: GraphQLProject
    user: GraphQLUser = strawberry.field(resolver=get_user_info)


@strawberry.input
class InputContribution:
    project: GraphQLInputProject


@strawberry.input
class ContributionFilter(BaseFilter):
    id: FilterBy | None = None
    uploaded_at: FilterBy | None = None
    user_id: FilterBy | None = None
    organization_id: FilterBy | None = None
