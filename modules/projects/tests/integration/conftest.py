import uuid

import lcax
import pytest
from beanie import WriteRules

from models import DBProject, DBContribution


@pytest.fixture()
async def projects(app, datafix_dir) -> list[DBProject]:
    projects = []

    for i in range(3):
        input_project = lcax.convert_lcabyg((datafix_dir / "project.json").read_text())
        assemblies = []
        for assembly in input_project.get("assemblies").values():
            assembly.update({"products": list(assembly.get("products").values())})
            assemblies.append(assembly)

        input_project.update({"assemblies": assemblies})

        project = DBProject(**input_project)
        project.id = uuid.uuid4()
        await project.insert(link_rule=WriteRules.WRITE)
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
