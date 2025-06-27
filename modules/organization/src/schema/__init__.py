from inspect import getdoc
from uuid import UUID

import strawberry

from models import GraphQLOrganization, GraphQLUser
from models.response import GraphQLResponse
from .organization import (
    add_organizations_mutation,
    edit_organizations_mutation,
    remove_organizations_mutation,
)
from .permisions import IsAuthenticated


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated], description="Returns all Organizations")
    async def organizations(self) -> GraphQLResponse[GraphQLOrganization]:
        return GraphQLResponse(GraphQLOrganization)


@strawberry.type
class Mutation:
    create_organizations: list[GraphQLOrganization] = strawberry.field(
        resolver=add_organizations_mutation,
        description=getdoc(add_organizations_mutation),
        permission_classes=[IsAuthenticated],
    )

    update_organizations: list[GraphQLOrganization] = strawberry.field(
        resolver=edit_organizations_mutation,
        description=getdoc(edit_organizations_mutation),
        permission_classes=[IsAuthenticated],
    )

    delete_organizations: list[UUID] = strawberry.field(
        resolver=remove_organizations_mutation,
        description=getdoc(remove_organizations_mutation),
        permission_classes=[IsAuthenticated],
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True, types=[GraphQLUser])
