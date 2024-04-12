from strawberry.types import Info

from models import DBProject, GraphQLProject


async def projects_query(info: Info) -> list[GraphQLProject]:
    """Returns all Projects"""

    projects = await DBProject.find_all().to_list()

    return projects


async def add_projects_mutation(info: Info, names: list[str]) -> list[GraphQLProject]:
    """Creates new Projects"""

    projects = []
    for name in names:
        project = DBProject(name=name)
        await project.insert()
        projects.append(project)

    return projects
