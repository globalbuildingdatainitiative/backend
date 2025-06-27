import pytest

from models import DBOrganization, CountryCodes, OrganizationMetaDataModel, StakeholderEnum


@pytest.fixture()
async def organizations(client, mongo) -> list[DBOrganization]:
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

    yield organizations
