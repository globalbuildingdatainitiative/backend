import pytest
import lcax

from logic import get_contributions, create_contributions
from models import InputContribution, GraphQLInputProject


@pytest.mark.asyncio
async def test_get_contributions(user, contributions):
    _contributions = await get_contributions(user.organization_id, None, None, 10, 0, fetch_links=False)

    assert _contributions
    assert len(_contributions) == len(contributions)


@pytest.mark.skip(reason="There is some issues serializing like Strawberry does.")
@pytest.mark.asyncio
async def test_create_contributions(user, datafix_dir):
    input_project = lcax.convert_lcabyg((datafix_dir / "project.json").read_text(), as_type=lcax.Project).model_dump(
        mode="json", by_alias=False
    )
    assemblies = []
    for assembly in input_project.get("assemblies").values():
        assembly.update({"products": list(assembly.get("products").values())})
        assemblies.append(assembly)

    input_project.update({"assemblies": assemblies})

    project = GraphQLInputProject(**input_project)
    inputs = [InputContribution(project=project)]

    _contributions = await create_contributions(inputs, user)

    assert _contributions
    assert len(_contributions) == 1
