from typing import Any

import pytest
import supertokens_python.recipe.usermetadata.asyncio

from models import DBOrganization, CountryCodes
from logic import ALLOWED_STAKEHOLDERS


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
async def organizations(app) -> list[DBOrganization]:
    organizations = []

    for i in range(3):
        organization = DBOrganization(
            name=f"Organization {i}",
            address=f"Address {i}",
            city=f"City {i}",
            country=CountryCodes.CAN,
            stakeholders=[ALLOWED_STAKEHOLDERS[i], ALLOWED_STAKEHOLDERS[i + 1]],
        )
        await organization.insert()
        organizations.append(organization)

    yield organizations
