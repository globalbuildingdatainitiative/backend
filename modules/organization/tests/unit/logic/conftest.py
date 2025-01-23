import pytest

from models import DBOrganization, CountryCodes, StakeholderEnum, OrganizationMetaDataModel


@pytest.fixture()
async def organizations(client) -> list[DBOrganization]:
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
