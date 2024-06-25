"""
from strawberry.types import Info

from logic import get_projects
from models import GraphQLProject


async def projects_query(info: Info) -> list[GraphQLProject]:
    # Returns all Projects

    projects = await get_projects()

    return projects
"""

from strawberry.types import Info
from logic import get_projects_counts_by_country
from models import ProjectAggregation, ProjectLocation


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
