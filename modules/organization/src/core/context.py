import logging
import uuid
from fastapi.requests import Request
from strawberry.types import Info
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata

from core.verify_jwt import verify_jwt
from models import SuperTokensUser

logger = logging.getLogger("main")


async def get_context(request: Request):
    from supertokens_python.recipe.session.asyncio import get_session

    session = await get_session(request, session_required=False)

    if not session:
        jwt = request.headers.get("Authorization")
        if jwt is None:
            return {"user": None}
        else:
            token = await verify_jwt(jwt.split("Bearer ")[1])
            generated_id = uuid.uuid5(uuid.NAMESPACE_URL, token.get("source"))
            logger.info(f"Generated user ID from JWT source: {generated_id}")
            return {"user": SuperTokensUser(id=generated_id, organization_id=None)}

    user_id = session.get_user_id()
    logger.info(f"Retrieved user ID from session: {user_id}")
    metadata = await get_user_metadata(user_id)
    organization_id = metadata.metadata.get("organization_id", None)

    return {"user": SuperTokensUser(id=user_id, organization_id=organization_id)}


def get_user(info: Info) -> SuperTokensUser:
    return info.context.get("user")
