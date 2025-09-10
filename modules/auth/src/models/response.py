import logging

import strawberry
from strawberry import Info

from core.context import get_user
from logic import get_users
from logic.roles import check_is_admin
from models import FilterBy, SortBy


logger = logging.getLogger("main")


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
        info: Info,
        filter_by: FilterBy | None = None,
        sort_by: SortBy | None = None,
        offset: int = 0,
        limit: int | None = strawberry.UNSET,
    ) -> list[T] | None:
        limit = (
            50 if limit == strawberry.UNSET else limit
        )  # Set default limit to 50 if it's not provided or set to None

        if self._type == "User":
            is_admin = await check_is_admin(get_user(info).id)
            logger.info(f"Is admin: {is_admin}")
            if is_admin:
                users = await get_users(filter_by, sort_by, limit, offset)
                logger.info(f"Got {len(users)} users as admin")
            else:
                filters = filter_by or FilterBy()
                org_id = get_user(info).organization_id or ""
                logger.info(f"filters {filters}")

                if filters.contains and not filters.contains.get("organization_id"):
                    filters.contains["organization_id"] = org_id
                elif filters.contains == strawberry.UNSET:
                    filters.contains = {"organization_id": org_id}

                users = await get_users(filters, sort_by, limit, offset)
                logger.info(f"Got {len(users)} users")

            return users

        return None

    @strawberry.field(description="Total number of items in the filtered dataset.")
    async def count(self, info: Info, filter_by: FilterBy | None = None) -> int:
        items = await self.items(info, filter_by=filter_by, limit=None)
        return len(items)
