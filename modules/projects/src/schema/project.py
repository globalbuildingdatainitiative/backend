from strawberry.types import Info
from logic import get_projects_counts_by_country, get_projects
from models import ProjectAggregation, ProjectLocation, ProjectFilters, ProjectSortOptions, GraphQLProject


async def projects_counts_by_country_query(info: Info) -> list[ProjectAggregation]:
    """Returns aggregated Projects with location and count by country"""

    projects = await get_projects_counts_by_country()
    return [
        ProjectAggregation(
            location=ProjectLocation(latitude=proj['latitude'], longitude=proj['longitude']),
            count=proj['count']
        )
        for proj in projects if proj.get('latitude') and proj.get('longitude')
    ]


async def get_projects_query(info: Info, filters: ProjectFilters = None, sort: ProjectSortOptions = None) -> list[GraphQLProject]:
    """Returns filtered and sorted Projects"""
    return await get_projects(filters, sort)
