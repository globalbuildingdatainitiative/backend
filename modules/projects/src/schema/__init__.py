from inspect import getdoc

import strawberry
from models import GraphQLProject
from schema.project import projects_query


@strawberry.type
class Query:
    projects: list[GraphQLProject] = strawberry.field(
        resolver=projects_query,
        description=getdoc(projects_query),
    )


@strawberry.type
class Mutation:
    ...


schema = strawberry.federation.Schema(query=Query)#, mutation=Mutation)
