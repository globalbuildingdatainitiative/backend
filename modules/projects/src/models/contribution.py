from uuid import UUID

import strawberry
from strawberry import UNSET

from .database.db_model import ContributionBase
from .openbdf import GraphQLProject, GraphQLInputProject
from .sort_filter import BaseFilter, FilterBy


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
    public: bool = False


@strawberry.input
class ContributionFilter(BaseFilter):
    id: FilterBy | None = None
    uploaded_at: FilterBy | None = None
    user_id: FilterBy | None = None
    organization_id: FilterBy | None = None
    public: FilterBy | None = None


@strawberry.input
class UpdateContribution:
    id: UUID
    public: bool | None = UNSET
