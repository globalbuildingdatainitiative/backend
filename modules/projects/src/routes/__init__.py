from schema import schema
from strawberry.fastapi import GraphQLRouter


def get_context():
    return {}


graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    path="/graphql",
    graphiql=True,
)
