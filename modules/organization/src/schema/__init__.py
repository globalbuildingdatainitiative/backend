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


@strawberry.type
class Query:
    organizations: list[GraphQLOrganization] = strawberry.field(
        resolver=organizations_query,
        description=getdoc(organizations_query),
    )


@strawberry.type
class Mutation:
    add_organizations: list[GraphQLOrganization] = strawberry.field(
        resolver=add_organizations_mutation,
        description=getdoc(add_organizations_mutation),
    )

    update_organizations: list[GraphQLOrganization] = strawberry.field(
        resolver=edit_organizations_mutation,
        description=getdoc(edit_organizations_mutation),
    )

    delete_organizations: list[UUID] = strawberry.field(
        resolver=remove_organizations_mutation,
        description=getdoc(remove_organizations_mutation),
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
