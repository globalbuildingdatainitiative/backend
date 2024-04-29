import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.framework.request import BaseRequest
from supertokens_python.recipe import emailpassword, session, dashboard, userroles, usermetadata
from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions, get_all_roles

from settings import settings

if "test" not in settings.SERVER_NAME.lower():
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

logger = logging.getLogger(__name__)

app = FastAPI(
    debug=True,
    title=settings.SERVER_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
)
app.add_middleware(get_middleware())


def get_origin(request: BaseRequest | None, user_context) -> str:
    logger.info(f"Request: {request}")
    if request is not None:
        origin = request.get_header("origin")
        logger.info(f"Origin: {origin}")
        if origin is None:
            # this means the client is in an iframe, it's a mobile app, or
            # there is a privacy setting on the frontend which doesn't send
            # the origin
            pass
        else:
            if origin.endswith("gbdi.io"):
                return origin
            elif origin.startswith("http://localhost"):
                return origin

    # in case the origin is unknown or not set, we return a default
    # value which will be used for this request.
    return "https://app.gbdi.io"

init(
    app_info=InputAppInfo(
        app_name=settings.SERVER_NAME,
        api_domain=str(settings.SERVER_HOST),
        api_base_path=f"{settings.API_STR}/auth",
        website_base_path="/auth",
        origin=get_origin
        #website_domain="http://localhost:8000"
    ),
    supertokens_config=SupertokensConfig(
        connection_uri=str(settings.CONNECTION_URI),
        api_key=settings.API_KEY
    ),
    framework='fastapi',
    recipe_list=[
        session.init(),
        emailpassword.init(),
        dashboard.init(),
        userroles.init(),
        usermetadata.init()
    ],
    mode='asgi'
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# async def on_startup():
#     await create_new_role_or_add_permissions("admin", ["read"])
#     logger.info(f"Available Roles: {', '.join((await get_all_roles()).roles)}")
