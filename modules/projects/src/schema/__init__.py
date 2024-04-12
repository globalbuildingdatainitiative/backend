from inspect import getdoc

import strawberry

from models import GraphQLProject
from schema.project import add_projects_mutation, projects_query


@strawberry.type
class Query:
    projects: list[GraphQLProject] = strawberry.field(
        resolver=projects_query,
        description=getdoc(projects_query),
    )


@strawberry.type
class Mutation:
    add_projects: list[GraphQLProject] = strawberry.field(
        resolver=add_projects_mutation,
        description=getdoc(add_projects_mutation),
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation)
