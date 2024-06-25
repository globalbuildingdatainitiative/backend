import strawberry


@strawberry.type
class ProjectLocation:
    latitude: float
    longitude: float


@strawberry.type
class ProjectAggregation:
    location: ProjectLocation
    count: int


@strawberry.input
class Aggregation:
    count: str
