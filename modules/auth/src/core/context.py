import logging
import uuid

from fastapi.requests import Request
from strawberry.types import Info
from jwt.exceptions import PyJWTError
from core.verify_jwt import verify_jwt
from models import SuperTokensUser
from core.cache import get_user_cache

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
    user_cache = get_user_cache()
    user = await user_cache.get_user(uuid.UUID(session.get_user_id()))

    # if not user:
    #     user = await user_cache.get_user(uuid.UUID(session.get_user_id()))
    # if not user:
    #     return {"user": None}
    if not user:
        logger.warning(f"User {session.get_user_id()} not found in cache, reloading cache")
        await user_cache.load_all()
        user = await user_cache.get_user(uuid.UUID(session.get_user_id()))
        if not user:
            logger.error(f"User {session.get_user_id()} still not found after cache reload")
            return {"user": None}
    return {"user": SuperTokensUser(id=user.id, organization_id=user.organization_id)}


def get_user(info: Info) -> SuperTokensUser:
    return info.context.get("user")
