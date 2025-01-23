import json
import uuid

import pytest
from beanie import WriteRules

from models import DBContribution
from models import DBProject


@pytest.fixture()
async def projects(datafix_dir) -> list[DBProject]:
    projects = []

    for i in range(3):
        input_project = json.loads((datafix_dir / "project.json").read_text())
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
