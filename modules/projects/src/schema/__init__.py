from inspect import getdoc
from uuid import UUID

import strawberry

from models import GraphQLContribution, GraphQLResponse, GraphQLProject, GraphQLUser
from schema.contribution import add_contributions_mutation, delete_contributions_mutation, update_contributions_mutation
from schema.permisions import IsAuthenticated


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated], description="Returns all projects of a user's organization")
    async def projects(self) -> GraphQLResponse[GraphQLProject]:
        return GraphQLResponse(GraphQLProject)

    @strawberry.field(
        permission_classes=[IsAuthenticated], description="Returns all contributions of a user's organization"
    )
    async def contributions(self) -> GraphQLResponse[GraphQLContribution]:
        return GraphQLResponse(GraphQLContribution)


@strawberry.type
class Mutation:
    add_contributions: list[GraphQLContribution] = strawberry.field(
        resolver=add_contributions_mutation,
        description=getdoc(add_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )
    delete_contributions: list[UUID] = strawberry.field(
        resolver=delete_contributions_mutation,
        description=getdoc(delete_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )
    update_contributions: list[GraphQLContribution] = strawberry.field(
        resolver=update_contributions_mutation,
        description=getdoc(update_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, types=[GraphQLUser], enable_federation_2=True)
