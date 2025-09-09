import json
import uuid

import pytest
from beanie import WriteRules

from models import DBProject, DBContribution


@pytest.fixture()
async def metadata_project(create_user, datafix_dir) -> list[DBProject]:
    input_project = json.loads((datafix_dir / "project_with_metadata.json").read_text())
    # Add the required createdBy field
    input_project["createdBy"] = str(create_user.id)
    project = DBProject(**input_project)
    project.id = uuid.uuid4()

    contribution = DBContribution(user_id=create_user.id, organization_id=create_user.organization_id, project=project)
    await contribution.insert(link_rule=WriteRules.WRITE)

    yield project


@pytest.fixture()
async def projects(app, datafix_dir, create_user) -> list[DBProject]:
    projects = []

    for i in range(3):
        input_project = json.loads((datafix_dir / "project.json").read_text())
        # Add the required createdBy field
        input_project["createdBy"] = str(create_user.id)
        project = DBProject(**input_project)
        project.id = uuid.uuid4()
        projects.append(project)

    yield projects


@pytest.fixture()
async def contributions(projects, create_user) -> list[DBContribution]:
    _contributions = []

    for i in range(3):
        contribution = DBContribution(
            user_id=create_user.id, organization_id=create_user.organization_id, project=projects[i]
        )
        await contribution.insert(link_rule=WriteRules.WRITE)
        _contributions.append(contribution)

    yield _contributions
