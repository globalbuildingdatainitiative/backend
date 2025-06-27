import strawberry
from strawberry import UNSET
from strawberry.scalars import JSON


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
