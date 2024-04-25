import pytest

from logic import get_contributions, create_contributions
from models import InputContribution


@pytest.mark.asyncio
async def test_get_contributions(user, contributions):

    _contributions = await get_contributions(user.organization_id)

    assert _contributions
    assert len(_contributions) == len(contributions)


@pytest.mark.asyncio
async def test_create_contributions(user, projects):

    inputs = [InputContribution(project=project) for project in projects]
    _contributions = await create_contributions(inputs, user)

    assert _contributions
    assert len(_contributions) == len(projects)
