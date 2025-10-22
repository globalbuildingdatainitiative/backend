import logging
import uuid

from fastapi.requests import Request
from strawberry.types import Info
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata
from jwt.exceptions import PyJWTError
from core.verify_jwt import verify_jwt
from models import SuperTokensUser
from core.cache import user_cache

logger = logging.getLogger("main")

MICROSERVICE_USER_ID = uuid.uuid5(uuid.NAMESPACE_URL, "microservice")

async def get_context(request: Request):
    from supertokens_python.recipe.session.asyncio import get_session

    session = await get_session(request, session_required=False)
    if not session:
        jwt = request.headers.get("Authorization")
        if jwt is None:
            return {"user": None}
        else:
            try:
                token = await verify_jwt(jwt.split("Bearer ")[1])
            except PyJWTError as error:
                logger.error(f"Error verifying JWT: {error}")
                raise
            if token.get("source") == "microservice":
                return {"user": SuperTokensUser(id=MICROSERVICE_USER_ID, organization_id=None)}
            return {
                "user": SuperTokensUser(id=uuid.uuid5(uuid.NAMESPACE_URL, token.get("source")), organization_id=None)
            }

    user = await user_cache.get_user(uuid.UUID(session.get_user_id()))
    
    return {"user": SuperTokensUser(id=user.id, organization_id=user.organization_id)}


def get_user(info: Info) -> SuperTokensUser:
    return info.context.get("user")
