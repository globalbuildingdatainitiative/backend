from inspect import getdoc

import strawberry

from models import GraphQLUser
from schema.permisions import IsAuthenticated
from schema.user import users_query, update_user_mutation


@strawberry.type
class Query:
    users: list[GraphQLUser] = strawberry.field(
        resolver=users_query, description=getdoc(users_query), permission_classes=[IsAuthenticated]
    )


@strawberry.type
class Mutation:
    update_user: GraphQLUser = strawberry.field(
        resolver=update_user_mutation, description=getdoc(update_user_mutation), permission_classes=[IsAuthenticated]
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
