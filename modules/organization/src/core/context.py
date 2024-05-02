from fastapi import Depends
from strawberry.types import Info
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata

from models import User


async def get_context(session: SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()
    metadata = await get_user_metadata(user_id)
    organization_id = metadata.metadata.get("organization_id", None)

    return {"user": User(id=user_id, organization_id=organization_id)}


def get_user(info: Info) -> User:
    return info.context.get("user")