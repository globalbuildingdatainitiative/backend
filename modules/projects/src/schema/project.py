from models import DBProject, GraphQLProject
from strawberry.types import Info


async def projects_query(info: Info) -> list[GraphQLProject]:
    """Returns all Projects"""

    projects = await DBProject.find_all().to_list()

    return projects