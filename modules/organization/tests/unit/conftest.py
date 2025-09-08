import pytest
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

from core.config import settings
from models import DBOrganization, CountryCodes, StakeholderEnum, OrganizationMetaDataModel


@pytest.fixture
async def mock_db():
    """Create a mock database for unit tests"""
    # Use mongomock for unit tests to avoid needing a real database
    client = AsyncMongoMockClient()
    db = client[settings.MONGO_DB]

    # Initialize Beanie with the mock database
    await init_beanie(database=db, document_models=[DBOrganization])

    yield db


@pytest.fixture
async def organizations(mock_db) -> list[DBOrganization]:
    """Creates sample organizations for unit tests"""
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
