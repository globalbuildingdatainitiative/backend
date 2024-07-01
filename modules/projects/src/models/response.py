from inspect import getdoc
from typing import List

import strawberry

from schema import projects_query


@strawberry.type
class GraphQLResponse[T]:
    items: List[T] | None = strawberry.field(
        description="The list of items in this pagination window."
    )
    count: int | None = strawberry.field(
        description="Total number of items in the filtered dataset."
    )
    groups: "GraphQLGroupResponse[T]" | None = strawberry.field()


@strawberry.type
class GraphQLGroupResponse[T]:
    group: str
    # TODO - fix this
    items: GraphQLResponse[T] | None = strawberry.field(resolver=projects_query, description=getdoc(projects_query))
