from inspect import getdoc
import strawberry

from models import GraphQLContribution, ProjectAggregation, GraphQLProject
from schema.contribution import add_contributions_mutation, contributions_query
from schema.permisions import IsAuthenticated
from .project import projects_counts_by_country_query, get_projects_query


@strawberry.type
class Query:
    projectsCountsByCountry: list[ProjectAggregation] = strawberry.field(
        resolver=projects_counts_by_country_query, description=getdoc(projects_counts_by_country_query),
        permission_classes=[IsAuthenticated]
    )
    contributions: list[GraphQLContribution] = strawberry.field(
        resolver=contributions_query, description=getdoc(contributions_query), permission_classes=[IsAuthenticated]
    )
    projects: list[GraphQLProject] = strawberry.field(
        resolver=get_projects_query, description="Returns filtered and sorted Projects",
        permission_classes=[IsAuthenticated]
    )


@strawberry.type
class Mutation:
    add_contributions: list[GraphQLContribution] = strawberry.field(
        resolver=add_contributions_mutation,
        description=getdoc(add_contributions_mutation),
        permission_classes=[IsAuthenticated],
    )


schema = strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True)
