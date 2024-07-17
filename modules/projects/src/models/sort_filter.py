import re
from typing import Type

import strawberry
from beanie import Document
from beanie.odm.queries.find import FindMany, FindQueryResultType
from strawberry.scalars import JSON


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]

    def items(self):
        return [(key, value) for key, value in self.dict().items() if value]


def filter_model_query(
    model: Type[Document], filters: BaseFilter, query: FindMany[FindQueryResultType] | None = None
) -> FindMany[FindQueryResultType]:
    if query is None:
        query = model.find_all(fetch_links=True)

    if filters:
        for _filter, fields in filters.items():
            for _field, value in fields.items():
                if not _field:
                    continue
                _field = to_snake(_field)

                field = getattr(model, _field)

                if _filter == "equal":
                    query = query.find(field == value)
                elif _filter == "is_true" and value is not None:
                    query = query.find(field is True)

    return query


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


def to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


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
            field = to_snake(field)

            if not hasattr(model, field):
                raise AttributeError(f"Field {field} does not exist in model {model}")

            if sort_direction == "dsc":
                query = query.sort(f"-{field}")
            else:
                query = query.sort(f"+{field}")

    return query


@strawberry.input
class FilterBy(BaseFilter):
    equal: JSON | None = None
    # contains: str | None = None
    # starts_with: str | None = None
    # ends_with: str | None = None
    # is_empty: bool | None = None
    # is_not_empty: bool | None = None
    # is_any_of: list[str] | None = None
    is_true: bool | None = None


@strawberry.input(one_of=True)
class SortBy(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET
