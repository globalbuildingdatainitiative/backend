from core.context import get_context
from schema import schema
from strawberry.fastapi import GraphQLRouter

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    path="/graphql",
    graphql_ide=True,
)
