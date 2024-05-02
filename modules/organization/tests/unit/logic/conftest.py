import pytest
from backend.modules.organization.src.models.organization import DBOrganization


@pytest.fixture()
async def organizations() -> list[DBOrganization]:
    organizations = []

    for i in range(3):
        organization = DBOrganization(name=f"Organization {i}")
        await organization.insert()
        organizations.append(organization)

    yield organizations

