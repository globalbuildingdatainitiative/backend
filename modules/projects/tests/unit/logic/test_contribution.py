import pytest
import lcax
from logic import get_contributions, create_contributions, get_contributions_for_header
from models import InputContribution, GraphQLInputProject
import datetime


@pytest.mark.asyncio
async def test_get_contributions(user, contributions):
    _contributions = await get_contributions(user.organization_id, None, None, 10, 0, fetch_links=False)

    assert _contributions
    assert len(_contributions) == len(contributions)


@pytest.mark.asyncio
async def test_get_contributions_for_header(user, contributions):
    header_data = await get_contributions_for_header(user.organization_id)

    assert header_data
    assert header_data.total_contributions == len(contributions)

    # Check days since last contribution
    last_contribution_date = contributions[-1].uploaded_at
    expected_days_since = (datetime.datetime.now() - last_contribution_date).days
    assert header_data.days_since_last_contribution == expected_days_since


@pytest.mark.skip(reason="There are some issues serializing like Strawberry does.")
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
