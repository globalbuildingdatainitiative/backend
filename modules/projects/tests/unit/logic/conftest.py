import json
import uuid

import pytest
from beanie import WriteRules

from models import DBContribution
from models import DBProject


@pytest.fixture()
async def projects(datafix_dir, create_user) -> list[DBProject]:
    projects = []

    for i in range(3):
        input_project = json.loads((datafix_dir / "project.json").read_text())
        input_project["id"] = str(uuid.uuid4())
        input_project["createdBy"] = str(create_user.id)  # Add required createdBy field
        project = DBProject(**input_project)
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
