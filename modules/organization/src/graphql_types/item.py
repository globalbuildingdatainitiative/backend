import strawberry


@strawberry.type
class GraphQLItem:
    id: strawberry.ID
    name: str
