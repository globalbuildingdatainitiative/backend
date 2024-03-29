from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from core.connection import get_db
from schema import schema


def get_context(session=Depends(get_db)):
    return {"session": session}


graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    path="/graphql",
    graphiql=True,
)
