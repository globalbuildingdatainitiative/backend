from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.framework.request import BaseRequest
from supertokens_python.recipe import session, userroles, usermetadata, emailpassword, dashboard
from supertokens_python.recipe.emailpassword import InputFormField
from supertokens_python.recipe.emailpassword.interfaces import APIInterface, APIOptions, SignUpPostOkResult
from supertokens_python.recipe.emailpassword.types import FormField
from typing import List, Dict, Any
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


def override_email_password_apis(original_implementation: APIInterface):
    original_sign_up_post = original_implementation.sign_up_post

    async def sign_up_post(
        form_fields: List[FormField], tenant_id, api_options: APIOptions, user_context: Dict[str, Any]
    ):
        # First we call the original implementation of sign_up_post
        response = await original_sign_up_post(form_fields, tenant_id, api_options, user_context)

        # Post sign up response, we check if it was successful
        if isinstance(response, SignUpPostOkResult):
            # Extract firstName and lastName from form_fields
            first_name = next(f.value for f in form_fields if f.id == "firstName")
            last_name = next(f.value for f in form_fields if f.id == "lastName")

            # Save metadata
            await usermetadata.asyncio.update_user_metadata(
                response.user.user_id, {"first_name": first_name, "last_name": last_name}
            )

        return response

    original_implementation.sign_up_post = sign_up_post
    return original_implementation


def supertokens_init():
    init(
        app_info=InputAppInfo(
            app_name=settings.SERVER_NAME,
            api_domain=str(settings.SERVER_HOST),
            api_base_path=f"{settings.API_STR}/auth",
            website_base_path="/auth",
            origin=get_origin,
        ),
        supertokens_config=SupertokensConfig(connection_uri=str(settings.CONNECTION_URI), api_key=settings.API_KEY),
        framework="fastapi",
        recipe_list=[
            session.init(),
            emailpassword.init(
                sign_up_feature=emailpassword.InputSignUpFeature(
                    form_fields=[
                        InputFormField(id="firstName"),
                        InputFormField(id="lastName"),
                    ]
                ),
                override=emailpassword.InputOverrideConfig(apis=override_email_password_apis),
            ),
            dashboard.init(),
            userroles.init(),
            usermetadata.init(),
        ],
        mode="asgi",
    )
