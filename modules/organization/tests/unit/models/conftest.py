import pytest

from models import DBOrganization, CountryCodes, OrganizationMetaDataModel, StakeholderEnum

from typing import AsyncIterator
from core.cache import get_organization_cache


@pytest.fixture()
async def organizations(client, mongo) -> AsyncIterator[list[DBOrganization]]:
    """Creates sample organizations before each test"""
    organizations = []

    for i in range(3):
        organization = DBOrganization(
            name=f"Organization {i}",
            address=f"Address {i}",
            city=f"City {i}",
            country=CountryCodes.CAN,
            meta_data=OrganizationMetaDataModel(
                stakeholders=[StakeholderEnum.BUILDING_USERS, StakeholderEnum.CIVIL_SOCIETY]
            ),
        )
        await organization.insert()
        organizations.append(organization)

    cache = get_organization_cache()
    await cache.load_all()
    await cache.get_all_organizations()

    yield organizations
