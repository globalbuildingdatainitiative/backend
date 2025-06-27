import logging
from typing import Type

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType
from strawberry import UNSET
from strawberry.scalars import JSON


logger = logging.getLogger("main")


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]

    def items(self):
        return [(key, value) for key, value in self.dict().items() if value]


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


def filter_model_query(
    model: Type[Document], filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all()

    for _filter, fields in filters.items():
        if not fields:
            continue

        for _field, value in fields.items():
            if not _field or value is UNSET:
                continue
            if _field == "id":
                _field = "_id"

            logger.debug(f"Filtering {_filter} by {_field} in {value}")

            if _filter == "contains":
                query = query.find({_field: {"$regex": f".*{value}.*", "$options": "i"}})
            elif _filter == "equal":
                query = query.find({_field: value})
            elif _filter == "not_equal":
                query = query.find({_field: {"$ne": value}})
            elif _filter == "is_true" and value is not None:
                query = query.find({_field: True})
            elif _filter == "_in":
                query = query.find({_field: {"$in": value}})
            elif _filter == "gt":
                query = query.find({_field: {"$gt": value}})
            elif _filter == "gte":
                query = query.find({_field: {"$gte": value}})
            elif _filter == "lt":
                query = query.find({_field: {"$lt": value}})
            elif _filter == "lte":
                query = query.find({_field: {"$lte": value}})

    return query


def sort_model_query(
    model: Type[Document], sort_by: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all()

    for sort_direction in ["asc", "dsc"]:
        field = getattr(sort_by, sort_direction)
        if not field:
            continue

        logger.debug(f"Sorting {field} by {sort_direction}")

        if sort_direction == "dsc":
            query = query.sort([(field, -1)])
        else:
            query = query.sort([(field, 1)])

    return query
