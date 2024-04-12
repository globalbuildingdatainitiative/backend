from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from schema import schema


def get_context():
    return {}


graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    path="/graphql",
    graphiql=True,
)
