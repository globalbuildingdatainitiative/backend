from inspect import getdoc
from uuid import UUID

import strawberry

from models import GraphQLOrganization
from .organization import (
    organizations_query,
    add_organizations_mutation,
    edit_organizations_mutation,
    remove_organizations_mutation,
)
from .permisions import IsAuthenticated


@strawberry.type
class Query:
    organizations: list[GraphQLOrganization] = strawberry.field(
        resolver=organizations_query, description=getdoc(organizations_query), permission_classes=[IsAuthenticated]
    )


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


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
