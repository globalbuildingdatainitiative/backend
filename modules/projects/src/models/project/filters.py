from typing import Any
from beanie.odm.queries.find import FindMany


class ProjectFilters:
    def __init__(self, **kwargs: Any):
        self.filters = kwargs

    def apply_filters(self, query: FindMany) -> FindMany:
        for key, value in self.filters.items():
            query = query.find({key: value})
        return query
