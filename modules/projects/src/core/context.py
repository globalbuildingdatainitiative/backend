from typing import TYPE_CHECKING
from uuid import UUID

from fastapi.requests import Request
from strawberry.types import Info
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata

if TYPE_CHECKING:
    from models import User


async def get_context(request: Request):
    from supertokens_python.recipe.session.asyncio import get_session
    from models import User

    session = await get_session(request, session_required=False)
    if not session:
        return {"user": None}

    user_id = session.get_user_id()
    metadata = await get_user_metadata(user_id)
    organization_id = metadata.metadata.get("organization_id", None)
    if organization_id:
        organization_id = UUID(organization_id)

    return {"user": User(id=UUID(user_id), organization_id=organization_id)}


def get_user(info: Info) -> "User":
    return info.context.get("user")
