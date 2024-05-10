import uuid

import lcax
import pytest

from models import DBProject, DBContribution


@pytest.fixture()
async def projects(mongo, datafix_dir) -> list[DBProject]:
    projects = []

    for i in range(3):
        project = DBProject(**lcax.convert_lcabyg((datafix_dir / f"project.json").read_text()))
        project.id = uuid.uuid4()
        await project.insert()
        projects.append(project)

    yield projects


@pytest.fixture()
async def contributions(projects, user) -> list[DBContribution]:
    _contributions = []

    for i in range(3):
        contribution = DBContribution(user_id=user.id, organization_id=user.organization_id, project=projects[i])
        await contribution.insert()
        _contributions.append(contribution)

    yield _contributions
