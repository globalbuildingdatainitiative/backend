from enum import Enum
from typing import Type, Annotated, TYPE_CHECKING

import strawberry
from strawberry import Info

if TYPE_CHECKING:
    from models import ProjectFilters, ProjectSort


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


@strawberry.input
class InputAggregation:
    method: AggregationMethod
    field: str


@strawberry.type
class AggregationResult:
    method: AggregationMethod
    field: str
    value: float | None


@strawberry.type
class GraphQLGroupResponse[T]:
    group: str

    # items: list[T] = strawberry.field()
    @strawberry.field()
    def items(self, limit: int | None = None) -> list[T]:
        return self.items

    @strawberry.field()
    async def aggregation(self, apply: list[InputAggregation]) -> list[AggregationResult]:
        return self.aggregation

    count: int


@strawberry.type
class GraphQLResponse[T]:
    def __init__(self, generic_type: Type[T]):
        self._generic_type = generic_type

    @property
    def _type(self):
        return self._generic_type._type_definition.name

    @strawberry.field(
        description="The list of items in this pagination window.",
    )
    async def items(
        self,
        filter_by: Annotated["ProjectFilters", strawberry.lazy("models")] = None,
        sort_by: Annotated["ProjectSort", strawberry.lazy("models")] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[T] | None:
        if self._type == "Project":
            from logic import get_projects

            return await get_projects(filter_by, sort_by, limit, offset)
        return None

    @strawberry.field(description="Total number of items in the filtered dataset.")
    async def count(self) -> int:
        return len(await self.items())

    @strawberry.field()
    async def groups(self, info: Info, group_by: str, limit: int = 50) -> list[GraphQLGroupResponse[T]]:
        if self._type == "Project":
            from models.project.methods import group_projects

            return await group_projects(
                group_by,
                limit,
                get_subselection_arguments(info, "items"),
                get_subselection_arguments(info, "aggregation"),
            )
        return []

    @strawberry.field()
    async def aggregation(self, apply: list[InputAggregation]) -> list[AggregationResult]:
        if self._type == "Project":
            from models.project.methods import aggregate_projects

            return await aggregate_projects(apply)
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
