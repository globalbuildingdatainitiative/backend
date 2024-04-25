import datetime

import pytest
from models import DBProject, DBContribution


@pytest.fixture()
async def projects(app) -> list[DBProject]:
    projects = []

    for i in range(3):
        project = DBProject(name=f"Project {i}")
        await project.insert()
        projects.append(project)

    yield projects


@pytest.fixture()
async def contributions(projects, user) -> list[DBContribution]:
    _contributions = []

    for i in range(3):
        contribution = DBContribution(user_id=user.id, organization_id=user.organization_id,
                                      uploaded_at=datetime.datetime.now(), project=projects[i])
        await contribution.insert()
        _contributions.append(contribution)

    yield _contributions
