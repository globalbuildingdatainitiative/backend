from enum import Enum

import strawberry


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


@strawberry.enum
class SortOptions(Enum):
    ASC = "asc"
    DSC = "dsc"
