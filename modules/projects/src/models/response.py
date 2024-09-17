from enum import Enum

import strawberry
from strawberry import Info
from strawberry.scalars import JSON

from core.context import get_user
from models.sort_filter import FilterBy, SortBy


@strawberry.enum
class AggregationMethod(Enum):
    AVG = "avg"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PCT25 = "pct25"
    PCT75 = "pct75"
    STD = "std"
    DIV = "div"


@strawberry.input
class InputAggregation:
    method: AggregationMethod
    field: str
    field2: str | None = None


@strawberry.type
class AggregationResult:
    method: AggregationMethod
    field: str
    value: float | None

    @strawberry.field()
    async def aggregation(self, apply: list[InputAggregation]) -> list["AggregationResult"]:
        return self.aggregation


@strawberry.type
class GraphQLGroupResponse[T]:
    group: str

    @strawberry.field()
    def items(self, limit: int | None = None) -> list[T]:
        return self.items

    @strawberry.field()
    async def aggregation(self, apply: list[InputAggregation]) -> list[AggregationResult]:
        return self.aggregation

    count: int


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
        user = get_user(info)
        organization_id = user.organization_id
        limit = (
            50 if limit == strawberry.UNSET else limit
        )  # Set default limit to 50 if it's not provided or set to None

        if self._type == "Project":
            from logic import get_projects

            return await get_projects(organization_id, filter_by, sort_by, limit, offset)
        elif self._type == "Contribution":
            from logic import get_contributions, check_fetch_projects

            return await get_contributions(
                organization_id, filter_by, sort_by, limit, offset, check_fetch_projects(info)
            )
        return None

    @strawberry.field(description="Total number of items in the filtered dataset.")
    async def count(self, info: Info, filter_by: FilterBy | None = None) -> int:
        items = await self.items(info, filter_by=filter_by, limit=None)
        return len(items)

    @strawberry.field()
    async def groups(self, info: Info, group_by: str, limit: int = 50) -> list[GraphQLGroupResponse[T]]:
        user = get_user(info)
        organization_id = user.organization_id

        if self._type == "Project":
            from models.project.methods import group_projects

            return await group_projects(
                organization_id,
                group_by,
                limit,
                get_subselection_arguments(info, "items"),
                get_subselection_arguments(info, "aggregation"),
            )
        return []

    @strawberry.field(
        description="Apply aggregation to the items. The aggregation should be specified in the 'apply' argument, which should be provided in MongoDB aggregation syntax."
    )
    async def aggregation(self, info: Info, apply: JSON) -> JSON:
        user = get_user(info)
        organization_id = user.organization_id

        if self._type == "Project":
            from models.project.methods import aggregate_projects

            return await aggregate_projects(organization_id, apply)
        return []


def get_subselection_arguments(info: Info, subselection: str) -> dict:
    fields = [field for field in info.selected_fields if field.name == "groups"]
    if not fields:
        return {}
    field = fields[0]
    items = [_field for _field in field.selections if _field.name == subselection]
    if not items:
        return {}
    return items[0].arguments
