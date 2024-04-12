import pytest
from models import DBProject


@pytest.fixture()
async def projects(mongo) -> list[DBProject]:
    projects = []

    for i in range(3):
        project = DBProject(name=f"Project {i}")
        await project.insert()
        projects.append(project)

    yield projects
