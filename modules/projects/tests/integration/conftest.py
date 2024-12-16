import json
import uuid

import pytest
from beanie import WriteRules

from models import DBProject, DBContribution, SuperTokensUser


@pytest.fixture()
async def metadata_project(app, user, datafix_dir) -> list[DBProject]:
    input_project = json.loads((datafix_dir / "project_with_metadata.json").read_text())
    project = DBProject(**input_project)
    project.id = uuid.uuid4()

    contribution = DBContribution(user_id=user.id, organization_id=user.organization_id, project=project)
    await contribution.insert(link_rule=WriteRules.WRITE)

    yield project


@pytest.fixture()
async def projects(app, datafix_dir) -> list[DBProject]:
    projects = []

    for i in range(3):
        input_project = json.loads((datafix_dir / "project.json").read_text())
        project = DBProject(**input_project)
        project.id = uuid.uuid4()
        projects.append(project)

    yield projects


@pytest.fixture(scope="session")
def user() -> SuperTokensUser:
    """Fixture to provide a mock SuperTokensUser."""
    return SuperTokensUser(id=uuid.uuid4(), organization_id=uuid.uuid4())


@pytest.fixture()
async def contributions(projects, user) -> list[DBContribution]:
    _contributions = []

    for i in range(3):
        contribution = DBContribution(user_id=user.id, organization_id=user.organization_id, project=projects[i])
        await contribution.insert(link_rule=WriteRules.WRITE)
        _contributions.append(contribution)

    yield _contributions
