from typing import Any, AsyncIterator

import pytest
from models import DBOrganization, CountryCodes, StakeholderEnum, OrganizationMetaDataModel
import supertokens_python.recipe.usermetadata.asyncio
from core.cache import get_organization_cache


@pytest.fixture(scope="session")
def mock_update_user_metadata(session_mocker):
    async def fake_update_user_metadata(
        user_id: str, metadata_update: dict[str, Any], user_context: dict[str, Any] | None = None
    ):
        pass

    session_mocker.patch.object(
        supertokens_python.recipe.usermetadata.asyncio,
        "update_user_metadata",
        fake_update_user_metadata,
    )


@pytest.fixture()
async def organizations(mongo) -> AsyncIterator[list[DBOrganization]]:
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
