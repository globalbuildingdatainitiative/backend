import pytest
from models import DBOrganization


@pytest.fixture()
async def organizations(app) -> list[DBOrganization]:
    organizations = []

    for i in range(3):
        organization = DBOrganization(name=f"Organization {i}")
        await organization.insert()
        organizations.append(organization)

    yield organizations
