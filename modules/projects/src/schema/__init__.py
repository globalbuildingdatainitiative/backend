from inspect import getdoc

import strawberry
from strawberry.types import Info

from models import GraphQLContribution, GraphQLResponse, GraphQLProject, ContributionHeaderData
from schema.contribution import add_contributions_mutation, get_contributions_for_header_resolver
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

    @strawberry.field(description="Fetch contribution header data")
    async def get_contributions_for_header(self, info: Info) -> ContributionHeaderData:
        return await get_contributions_for_header_resolver(info)


@strawberry.type
class Mutation:
    add_contributions: list[GraphQLContribution] = strawberry.field(
        resolver=add_contributions_mutation,
        description=getdoc(add_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
