from inspect import getdoc

import strawberry

from models import GraphQLProject, GraphQLContribution
from schema.contribution import add_contributions_mutation, contributions_query
from schema.permisions import IsAuthenticated
from schema.project import projects_query


@strawberry.type
class Query:
    projects: list[GraphQLProject] = strawberry.field(
        resolver=projects_query, description=getdoc(projects_query), permission_classes=[IsAuthenticated]
    )
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
