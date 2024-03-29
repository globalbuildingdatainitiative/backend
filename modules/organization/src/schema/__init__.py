from inspect import getdoc

import strawberry

from graphql_types.item import GraphQLItem
from schema.item import add_item_mutation, items_query


@strawberry.type
class Query:
    items: list[GraphQLItem] = strawberry.field(
        resolver=items_query,
        description=getdoc(items_query),
    )


@strawberry.type
class Mutation:
    add_item: GraphQLItem = strawberry.field(
        resolver=add_item_mutation,
        description=getdoc(add_item_mutation),
    )


schema = strawberry.Schema(query=Query, mutation=Mutation)
