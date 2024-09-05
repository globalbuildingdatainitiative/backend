from uuid import UUID

import httpx
from async_lru import alru_cache
from pydantic import BaseModel

from core.exceptions import MicroServiceConnectionError
from models import DBProject
from models.response import AggregationMethod, InputAggregation


class ProjectAggregation(BaseModel):
    method: AggregationMethod
    field: str
    value: float | None


class ProjectGroup(BaseModel):
    group: str
    items: list[DBProject]
    aggregation: list[ProjectAggregation] | None = None
    count: int


async def group_projects(organization_id: UUID, group_by: str, limit: int, items_args: dict, aggregation_args: dict):
    from models import DBProject

    items = {"$push": "$$ROOT"}
    if items_args.get("limit"):
        items = {"$topN": {"n": int(items_args.get("limit")), "output": "$$ROOT", "sortBy": {"_id": -1}}}

    aggregation = {}
    projection = {
        "$project": {
            "_id": None,
            "group": group_by,
            "items": "$items",
            "count": "$count",
        }
    }
    if aggregation_args:
        aggregation_projection = []
        for _input in aggregation_args.get("apply"):
            field = _input.get("field")
            method = _input.get("method").lower()
            key = f"{method}_{field.replace(".", "_")}"
            if method == "pct25":
                aggregation[key] = {"$percentile": {"input": f"${field}", "p": [0.25], "method": "approximate"}}
                aggregation_projection.append({"method": method, "value": {"$first": f"${key}"}, "field": field})
            elif method == "pct75":
                aggregation[key] = {"$percentile": {"input": f"${field}", "p": [0.75], "method": "approximate"}}
                aggregation_projection.append({"method": method, "value": {"$first": f"${key}"}, "field": field})
            elif method == "median":
                aggregation[key] = {"$median": {"input": f"${field}", "method": "approximate"}}
                aggregation_projection.append({"method": method, "value": f"${key}", "field": field})
            else:
                aggregation[key] = {f"${method}": f"${field}"}
                aggregation_projection.append({"method": method, "value": f"${key}", "field": field})
        projection["$project"]["aggregation"] = aggregation_projection

    groups = (
        await DBProject.find(DBProject.contribution.organization_id == organization_id, fetch_links=True)
        .aggregate(
            [
                {"$group": {"_id": f"${group_by}", "items": items, "count": {"$sum": 1}, **aggregation}},
                projection,
                {"$limit": limit},
            ],
            projection_model=ProjectGroup,
        )
        .to_list()
    )
    return groups



async def group_projects2(organization_id: UUID, group_by: str, limit: int, items_args: dict, aggregation: dict):
    from models import DBProject

    items = {"$push": "$$ROOT"}
    if items_args.get("limit"):
        items = {"$topN": {"n": int(items_args.get("limit")), "output": "$$ROOT", "sortBy": {"_id": -1}}}

    projection = {
        "$project": {
            "_id": None,
            "group": group_by,
            "items": "$items",
            "count": "$count",
        }
    }

    groups = (
        await DBProject.find(DBProject.contribution.organization_id == organization_id, fetch_links=True)
        .aggregate(
            [
                {"$group": {"_id": f"${group_by}", "items": items, "count": {"$sum": 1}, **aggregation}},
                projection,
                {"$limit": limit},
            ],
        )
        .to_list()
    )
    return groups


async def aggregate_projects(organization_id: UUID, apply: list[InputAggregation]):
    groups = []
    for _input in apply:
        agg = (
            await DBProject.find(DBProject.contribution.organization_id == organization_id, fetch_links=True)
            .aggregate(
                [{"$group": {"_id": None, "value": {f"${_input.method.value}": f"${_input.field}"}}}],
            )
            .to_list()
        )
        groups.append(ProjectAggregation(method=_input.method, value=agg[0].get("value"), field=_input.field))
    return groups

async def aggregate_projects2(organization_id: UUID, apply: list[dict]):
    groups = await DBProject.find(DBProject.contribution.organization_id == organization_id, fetch_links=True).aggregate(apply).to_list()
    return groups


@alru_cache
async def get_coordinates(country_name: str) -> dict:
    country_name = country_name.lower()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://nominatim.openstreetmap.org/search?q={country_name}&format=json")
        except httpx.RequestError as e:
            raise MicroServiceConnectionError(f"Could not connect to nominatim.openstreetmap.org. Got {e}")
        if response.is_error:
            raise MicroServiceConnectionError(
                f"Could not receive data from nominatim.openstreetmap.org. Got {response.text}"
            )
        data = response.json()[0]
        return {"latitude": float(data["lat"]), "longitude": float(data["lon"])}
    return {"latitude": None, "longitude": None}
