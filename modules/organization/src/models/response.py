import strawberry

from logic import get_organizations
from models import FilterBy, SortBy


@strawberry.type
class GraphQLResponse[T]:
    def __init__(self, generic_type: type[T]):
        self._generic_type = generic_type

    @property
    def _type(self):
        return self._generic_type._type_definition.name

    @strawberry.field(
        description="The list of items in this pagination window.",
    )
    async def items(
        self,
        filter_by: FilterBy | None = None,
        sort_by: SortBy | None = None,
        offset: int = 0,
        limit: int | None = strawberry.UNSET,
    ) -> list[T] | None:
        limit = (
            50 if limit == strawberry.UNSET else limit
        )  # Set default limit to 50 if it's not provided or set to None

        if self._type == "Organization":
            return await get_organizations(filter_by, sort_by, limit, offset)

        return None

    @strawberry.field(description="Total number of items in the filtered dataset.")
    async def count(self, filter_by: FilterBy | None = None) -> int:
        items = await self.items(filter_by=filter_by, limit=None)
        return len(items)
