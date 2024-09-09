import json
from uuid import UUID

from bson import DBRef
from orjson import orjson
from strawberry.http import GraphQLHTTPResponse

from core.context import get_context
from schema import schema
from strawberry.fastapi import GraphQLRouter

class GBDIRouter(GraphQLRouter):
    def encode_json(self, data: GraphQLHTTPResponse) -> bytes:
        # class UUIDEncoder(json.JSONEncoder):
        #     def default(self, obj):
        #         if isinstance(obj, UUID):
        #             # if the obj is uuid, we simply return the value of uuid
        #             return str(obj)
        #         return json.JSONEncoder.default(self, obj)
        #
        # return json.dumps(data, cls=UUIDEncoder)
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
