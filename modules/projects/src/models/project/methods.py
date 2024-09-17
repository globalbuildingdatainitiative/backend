import json
from pathlib import Path
from uuid import UUID

import httpx
from async_lru import alru_cache
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.exceptions import MicroServiceConnectionError, ThrottleError
from models import DBProject
from models.response import AggregationMethod
import logging

logger = logging.getLogger(__name__)


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
            "group": "$_id",
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
        await DBProject.find(DBProject.contribution.organizationId == organization_id, fetch_links=True)
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


async def aggregate_projects(organization_id: UUID, apply: list[dict]):
    groups = (
        await DBProject.find(DBProject.contribution.organizationId == organization_id, fetch_links=True)
        .aggregate(apply)
        .to_list()
    )
    return groups


@alru_cache
async def get_coordinates(country_name: str, city_name: str | None = None) -> dict:
    country_name = country_name.lower()
    city_name = city_name.lower() if city_name else None

    if city_name:
        return await get_city_location(city_name)
    else:
        country_cache = json.loads((Path(__file__).parent / "country_cache.json").read_text())
        if country_cache.get(country_name):
            return country_cache.get(country_name)

    return {"latitude": 0.0, "longitude": 0.0}


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(ThrottleError),
)
async def get_city_location(city_name: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json")
        except httpx.RequestError as e:
            raise MicroServiceConnectionError(f"Could not connect to nominatim.openstreetmap.org. Got {e}")
        if response.is_error:
            if "Bandwidth Limit exceeded" in response.text:
                logger.info(f"Bandwidth Limit Exceeded - {city_name}")
                raise ThrottleError("Bandwidth Limit Exceeded")
            else:
                raise MicroServiceConnectionError(
                    f"Could not receive data from nominatim.openstreetmap.org. Got {response.text}"
                )
        _json = response.json()
        if _json:
            data = _json[0]
            return {"latitude": float(data["lat"]), "longitude": float(data["lon"])}
        return {"latitude": 0.0, "longitude": 0.0}
