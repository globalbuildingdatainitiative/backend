import strawberry


@strawberry.input
class FilterOptions:
    equal: str | None = None
    contains: str | None = None
    starts_with: str | None = None
    ends_with: str | None = None
    is_true: bool | None = None


class BaseFilter:  # pragma: no cover
    def dict(self):
        return self.__dict__

    def keys(self):
        return [key for key, value in self.dict().items() if value]


@strawberry.input(one_of=True)
class SortBy(BaseFilter):
    asc: str | None = strawberry.UNSET
    dsc: str | None = strawberry.UNSET
