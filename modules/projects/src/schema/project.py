from strawberry.types import Info

from logic import get_projects
from models import ProjectFilters, GraphQLResponse, ProjectSort, GraphQLProject


async def projects_query(info: Info, filter_by: ProjectFilters | None = None, sort_by: ProjectSort | None = None,
                         limit: int = 50,
                         offset: int | None = None) -> GraphQLResponse[GraphQLProject]:
    """Query projects in the database"""

    projects = await get_projects(filter_by, sort_by, limit, offset)

    return GraphQLResponse(items=projects, count=len(projects))



"""
projects(filter, sort, limit, pagination) -> [Project]


aggregate(model: Project, method: avg,max,min,sum, field: String) -> number


type Project {
  ...
}

type ProjectResponse {
  pageInfo: PageInfo
  list: ProjectList
  groups(groupBy: GroupByProject): [ProjectGroup!]
  aggregation(method: Method, field: String)
  count: Int!
}

type ProjectGroup {
  group: String!
  items(limit): [ProjectResponse]!
  count: Int!
}

type PageInfo {
  hasNextPage: Boolean
  hasPreviousPage: Boolean
  startCursor: String
  endCursor: String
}

type ProjectEdge {
  item: Project!
  cursor: String!
}

type Method {
 avg
 max
 min
 sum
}

query aggregateProject(filter): ProjectAggregation!

type ProjectAggregation {
  id(method: Method): String
  location {
    country(method: Method)
    latitude
    longitude
  }
}
"""