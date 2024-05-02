from enum import Enum

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType


@strawberry.input
class FilterOptions:
    equal: str | None = None
    # contains: str | None = None
    # starts_with: str | None = None
    # ends_with: str | None = None
    # is_empty: bool | None = None
    # is_not_empty: bool | None = None
    # is_any_of: list[str] | None = None
    is_true: bool | None = None


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]


def filter_model_query(
        model: Document, filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all()

    for filter_key in filters.keys():
        _filter = getattr(filters, filter_key)
        field = getattr(model, filter_key)

        if _filter.equal:
            query = query.find(field == _filter.equal)
        elif _filter.is_true is not None:
            query = query.find(field == _filter.is_true)

    return query


@strawberry.enum
class SortOptions(Enum):
    ASC = "asc"
    DSC = "dsc"


def sort_model_query(
        model: Document, sorters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all()

    for sort_key in sorters.keys():
        sort_by = getattr(sorters, sort_key)
        field = getattr(model, sort_key)

        if sort_by == SortOptions.DSC:
            query = query.sort(f"-{field}")
        else:
            query = query.sort(f"+{field}")

    return query
