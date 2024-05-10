from strawberry.types import Info

from logic import get_projects
from models import GraphQLProject


async def projects_query(info: Info) -> list[GraphQLProject]:
    """Returns all Projects"""

    projects = await get_projects()

    return projects
