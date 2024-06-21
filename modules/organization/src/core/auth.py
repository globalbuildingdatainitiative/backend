from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.framework.request import BaseRequest
from supertokens_python.recipe import session, userroles, usermetadata, jwt

from core.config import settings


def get_origin(request: BaseRequest | None, user_context) -> str:
    if request is not None:
        origin = request.get_header("origin")
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


def supertokens_init():
    init(
        app_info=InputAppInfo(
            app_name=settings.SERVER_NAME,
            api_domain=str(settings.SERVER_HOST),
            api_base_path=f"{settings.API_STR}/auth",
            website_base_path="/auth",
            origin=get_origin,
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=str(settings.SUPERTOKENS_CONNECTION_URI), api_key=settings.SUPERTOKENS_API_KEY
        ),
        framework="fastapi",
        recipe_list=[session.init(), userroles.init(), usermetadata.init(), jwt.init()],
        mode="asgi",
    )
