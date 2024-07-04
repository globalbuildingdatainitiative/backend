from enum import Enum
from typing import List, Type, TYPE_CHECKING, Annotated

import strawberry
from pydantic import BaseModel, Field
from strawberry.scalars import JSON

if TYPE_CHECKING:
    from models import ProjectFilters, ProjectSort


async def group_projects(group_by: str):
    from models import DBProject
    class ProjectGroup(BaseModel):
        group: str = Field(None, alias="_id")
        items: List[DBProject]
        count: int

    groups = await DBProject.find_all().aggregate(
        [{
            "$group": {
                "_id": f"${group_by}",
                "items": {"$push": "$$ROOT"},
                "count": {"$sum": 1}
            }
        }],
        projection_model=ProjectGroup
    ).to_list()
    return groups


async def aggregate_projects(group_by: str):
    from models import DBProject
    class ProjectAggregation(BaseModel):
        method: str = Field(None, alias="_id")
        field: str
        value: float | None

    groups = await DBProject.find_all().aggregate(
        [{
            "$group": {
                "_id": None,
                "value": {"$avg": "$reference_study_period"},
                "field": "field"
            }
        }],
        # TODO - Fix this
        projection_model=ProjectAggregation
    ).to_list()
    return groups


@strawberry.type
class GraphQLGroupResponse[T]:
    group: str
    items: list[T]
    count: int


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
    value: float


@strawberry.type
class GraphQLResponse[T]:
    def __init__(self, generic_type: Type[T]):
        self._generic_type = generic_type

    @strawberry.field(description="The list of items in this pagination window.", )
    async def items(self, filter_by: Annotated["ProjectFilters", strawberry.lazy("models")] = None,
                    sort_by: Annotated["ProjectSort", strawberry.lazy("models")] = None,
                    offset: int = 0, limit: int = 50) -> list[T] | None:
        if self._generic_type._type_definition.name == "Project":
            from logic import get_projects
            return await get_projects(filter_by, sort_by, limit, offset)
        return None

    @strawberry.field(description="Total number of items in the filtered dataset.")
    async def count(self) -> int:
        return len(await self.items())

    @strawberry.field()
    async def groups(self, group_by: str) -> list[GraphQLGroupResponse[T]]:
        return await group_projects(group_by)

    @strawberry.field()
    async def aggregation(self, apply: list[InputAggregation]) -> AggregationResult:
        return await aggregate_projects(apply)
