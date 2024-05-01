from inspect import getdoc

import strawberry

from models import GraphQLUser
from schema.user import users_query


@strawberry.type
class Query:
    users: list[GraphQLUser] = strawberry.field(
        resolver=users_query,
        description=getdoc(users_query),
    )


schema = strawberry.federation.Schema(query=Query, enable_federation_2=True)
