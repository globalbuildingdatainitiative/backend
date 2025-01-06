import re
from logging import getLogger
from typing import Type
from uuid import UUID

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType
from strawberry import UNSET
from strawberry.scalars import JSON
from iso3166 import countries as iso_countries

logger = getLogger("main")


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]

    def items(self):
        return [(key, value) for key, value in self.dict().items() if value]


def get_matching_country_codes(search_text: str) -> list[str]:
    """Get country codes that match the search text"""
    matching_codes = []
    search_text = search_text.lower()

    for country in iso_countries:
        if search_text in country.name.lower():
            matching_codes.append(country.alpha3.lower())

    return matching_codes


def filter_model_query(
    model: Type[Document], filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    if filters:
        for _filter, fields in filters.items():
            if not fields:
                continue

            for _field, value in fields.items():
                if not _field or value is UNSET:
                    continue

                # Handle special case for country field
                if _field in ["countryName", "project.location.countryName"]:
                    field_path = "project.location.country"
                    if _filter == "contains":
                        matching_codes = get_matching_country_codes(value)
                        if matching_codes:
                            query = query.find({field_path: {"$in": matching_codes}})
                        else:
                            # If no matches found, ensure no results are returned
                            query = query.find({"_id": None})
                    continue

                # Map other field names to database paths
                field_mapping = {
                    "name": "project.name",
                    "buildingType": "project.projectInfo.buildingType",
                    "uploadedAt": "uploadedAt",
                    "public": "public",  # Not working
                    "organization_id": "organization_id",
                    "id": "_id",
                    "_id": "_id",
                    "lifeCycleStages": "project.lifeCycleStages",
                    "impactCategories": "project.impactCategories",
                }

                field_path = field_mapping.get(_field, _field)

                logger.debug(f"Filtering {_filter} by {field_path} in {value}")

                # Handle UUID fields specially
                if isinstance(value, UUID) or (isinstance(value, str) and len(value) == 36):
                    if _filter == "equal":
                        if isinstance(value, str):
                            try:
                                value = UUID(value)
                            except ValueError:
                                continue
                        query = query.find({field_path: value})
                else:
                    # Handle other field types
                    if _filter == "contains":
                        query = query.find({field_path: {"$regex": f".*{value}.*", "$options": "i"}})
                    elif _filter == "equal":
                        query = query.find({field_path: value})
                    elif _filter == "not_equal":
                        query = query.find({field_path: {"$ne": value}})
                    elif _filter == "is_true" and value is not None:
                        query = query.find({field_path: True})
                    elif _filter == "_in":
                        query = query.find({field_path: {"$in": value}})
                    elif _filter == "gt":
                        query = query.find({field_path: {"$gt": value}})
                    elif _filter == "gte":
                        query = query.find({field_path: {"$gte": value}})
                    elif _filter == "lt":
                        query = query.find({field_path: {"$lt": value}})
                    elif _filter == "lte":
                        query = query.find({field_path: {"$lte": value}})

    return query


def sort_model_query(
    model: Type[Document], sort_by: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    if sort_by:
        for sort_direction in ["asc", "dsc"]:
            field = getattr(sort_by, sort_direction)
            if not field:
                continue

            # Map frontend field paths to database paths
            field_mappings = {
                # "name": "project.name",  # Not working
                "project.location.countryName": "project.location.country",
                "project.projectInfo.buildingType": "project.projectInfo.buildingType",
                "uploadedAt": "uploadedAt",
                "public": "public",
                "project.lifeCycleStages": "project.lifeCycleStages",
                "project.impactCategories": "project.impactCategories",
            }

            # Get the correct field path or use the original if no mapping exists
            field_path = field_mappings.get(field, field)

            logger.debug(f"Sorting {field_path} by {sort_direction}")

            # Add sort to existing query
            if sort_direction == "dsc":
                query = query.sort([(field_path, -1)])
            else:
                query = query.sort([(field_path, 1)])

    return query


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


@strawberry.input
class FilterBy(BaseFilter):
    equal: JSON | None = UNSET
    contains: JSON | None = UNSET
    starts_with: JSON | None = UNSET
    ends_with: JSON | None = UNSET
    gt: JSON | None = UNSET
    gte: JSON | None = UNSET
    lt: JSON | None = UNSET
    lte: JSON | None = UNSET
    not_equal: JSON | None = UNSET
    is_true: bool | None = UNSET
    _in: JSON | None = strawberry.field(name="in", default=UNSET)


@strawberry.input(one_of=True)
class SortBy(BaseFilter):
    asc: str | None = UNSET
    dsc: str | None = UNSET
