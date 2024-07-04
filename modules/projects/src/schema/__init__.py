from inspect import getdoc

import strawberry

from models import GraphQLContribution, GraphQLResponse, GraphQLProject
from schema.contribution import add_contributions_mutation, contributions_query
from schema.permisions import IsAuthenticated


@strawberry.type
class Query:
    @strawberry.field
    async def projects(self) -> GraphQLResponse[GraphQLProject]:
        return GraphQLResponse(GraphQLProject)

    contributions: list[GraphQLContribution] = strawberry.field(
        resolver=contributions_query, description=getdoc(contributions_query), permission_classes=[IsAuthenticated]
    )


@strawberry.type
class Mutation:
    add_contributions: list[GraphQLContribution] = strawberry.field(
        resolver=add_contributions_mutation,
        description=getdoc(add_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
