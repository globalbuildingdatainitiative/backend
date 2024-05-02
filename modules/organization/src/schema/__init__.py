from inspect import getdoc

import strawberry

from ..models import GraphQLOrganization
from ..schema.organization import organization_query, create_organization_mutation, update_organization_mutation, \
    delete_organization_mutation


@strawberry.type
class Query:
    organizations: list[GraphQLOrganization] = strawberry.field(
        resolver=organization_query,
        description=getdoc(organization_query),
    )


@strawberry.type
class Mutation:
    create_organization: list[GraphQLOrganization] = strawberry.field(
        resolver=create_organization_mutation,
        description=getdoc(create_organization_mutation),
    )

    update_organization: list[GraphQLOrganization] = strawberry.field(
        resolver=update_organization_mutation,
        description=getdoc(update_organization_mutation),
    )

    delete_organization: list[GraphQLOrganization] = strawberry.field(
        resolver=delete_organization_mutation,
        description=getdoc(delete_organization_mutation),
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
