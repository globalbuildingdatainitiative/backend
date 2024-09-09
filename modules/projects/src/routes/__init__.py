from bson import DBRef
from orjson import orjson
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse

from core.context import get_context
from schema import schema


class GBDIRouter(GraphQLRouter):
    def encode_json(self, data: GraphQLHTTPResponse) -> bytes:
        def default(obj):
            if isinstance(obj, DBRef):
                return str(obj.id)
            raise TypeError

        return orjson.dumps(data, default=default)


graphql_app = GBDIRouter(
    schema,
    context_getter=get_context,
    path="/graphql",
    graphiql=True,
)
