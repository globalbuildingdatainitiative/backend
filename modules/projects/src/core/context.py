from typing import TYPE_CHECKING
from uuid import UUID

from fastapi.requests import Request
from strawberry.types import Info
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata
from supertokens_python.recipe.userroles.asyncio import get_roles_for_user

if TYPE_CHECKING:
    from models import SuperTokensUser


async def get_context(request: Request):
    from supertokens_python.recipe.session.asyncio import get_session
    from models import SuperTokensUser as User
    from backend.modules.auth.src.models.roles import Role

    session = await get_session(request, session_required=False)
    if not session:
        return {"user": None}

    user_id = session.get_user_id()
    metadata = await get_user_metadata(user_id)
    organization_id = metadata.metadata.get("organization_id", None)
    if organization_id:
        organization_id = UUID(organization_id)
    
    # Get user roles from SuperTokens
    roles_response = await get_roles_for_user("public", user_id)
    roles = [Role(role) for role in roles_response.roles]

    return {"user": User(id=UUID(user_id), organization_id=organization_id, roles=roles)}


def get_user(info: Info) -> "SuperTokensUser":
    return info.context.get("user")
