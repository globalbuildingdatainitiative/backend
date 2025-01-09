import logging
from typing import List, Dict, Any, Union
from uuid import UUID

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.framework.request import BaseRequest
from supertokens_python.ingredients.emaildelivery.types import (
    EmailDeliveryConfig,
    SMTPSettings,
    SMTPSettingsFrom,
    EmailContent,
)
from supertokens_python.recipe import session, userroles, usermetadata, emailpassword, dashboard, jwt, emailverification
from supertokens_python.recipe.emailpassword import InputFormField
from supertokens_python.recipe.emailpassword.asyncio import get_user_by_id
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface,
    APIOptions,
    SignUpPostOkResult,
    RecipeInterface,
    SignInOkResult,
    SignInWrongCredentialsError,
    ResetPasswordUsingTokenOkResult,
    ResetPasswordUsingTokenInvalidTokenError,
)
from supertokens_python.recipe.emailpassword.types import FormField, PasswordResetEmailTemplateVars, SMTPOverrideInput
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata, update_user_metadata

from core.config import settings

FAKE_PASSWORD = "asokdA87fnf30efjoiOI**cwjkn"
LOGO_URL = "https://app.gbdi.io/favicon.png"
logger = logging.getLogger("main")


def get_origin(request: BaseRequest | None, user_context) -> str:
    request = request or user_context.get("request")
    if request is not None:
        if isinstance(request, BaseRequest):
            origin = request.get_header("origin")
        else:
            origin = request.headers.get("origin")

        if origin is None:
            pass
        else:
            if origin.endswith("gbdi.io"):
                return origin
            elif origin.startswith("http://localhost"):
                return origin

    return "https://app.gbdi.io"


# SMTP Configuration
smtp_settings = SMTPSettings(
    host=settings.SMTP_HOST,
    port=settings.SMTP_PORT,
    from_=SMTPSettingsFrom(name=settings.SMTP_NAME, email=settings.SMTP_EMAIL),
    password=settings.SMTP_PASSWORD,
    secure=False,
    username=settings.SMTP_USERNAME,
)


def custom_smtp_content_override(original_implementation: SMTPOverrideInput) -> SMTPOverrideInput:
    """Overrides email content for password reset emails"""

    async def get_content(template_vars: PasswordResetEmailTemplateVars, user_context: Dict[str, Any]) -> EmailContent:
        from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata
        from logic import get_organization_name

        user_id = template_vars.user.id
        user_metadata = await get_user_metadata(user_id)
        inviter_id = user_metadata.metadata.get("inviter_id")
        organization_id = user_metadata.metadata.get("pending_org_id")
        password_reset_url = template_vars.password_reset_link

        subject = "Reset Your Password"
        body = ""
        is_html = True

        if inviter_id and organization_id:
            inviter_metadata = await get_user_metadata(inviter_id)
            inviter_name = f"{inviter_metadata.metadata.get('first_name', '')} {inviter_metadata.metadata.get('last_name', '')}".strip()
            organization_name = await get_organization_name(UUID(organization_id))

            subject = f"Invitation to join {organization_name}"

            accept_signin_url = f"{get_origin(None, user_context)}/accept-invite?user_id={user_id}"
            reject_url = f"{get_origin(None, user_context)}/reject-invite?user_id={user_id}"
            accept_new_user_url = f"{get_origin(None, user_context)}/accept-invite-new?user_id={user_id}"

            body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Invitation to join {organization_name}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #E6E6E6;
                        background-color: #1C1C1C;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .header {{
                        background-color: #1d9a78;
                        padding: 20px;
                        border-radius: 5px;
                        position: relative;
                    }}
                    .header-content {{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        position: relative;
                        max-width: 80%;
                        margin: 0 auto;
                    }}
                    .header h1 {{
                        color: white;
                        font-size: 24px;
                        margin: 0;
                    }}
                    .logo {{
                        width: 80px;
                        height: auto;
                        margin-left: 20px;
                    }}
                    .content {{
                        padding: 20px 0;
                    }}
                    p {{
                        margin: 16px 0;
                        font-size: 16px;
                    }}
                    .button {{
                        display: inline-block;
                        background-color: #1d9a78;
                        color: white;
                        text-decoration: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        margin-right: 10px;
                        margin-top: 10px;
                    }}
                    .reject-button {{
                        background-color: #cc4125;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="header-content">
                            <h1>Invitation to Join {organization_name}</h1>
                            <img src="{LOGO_URL}" alt="{organization_name} Logo" class="logo">
                        </div>
                    </div>
                    <div class="content">
                        <p>Dear Invitee,</p>
                        <p>You have been invited by {inviter_name} to join the organization {organization_name}.</p>
                        <p>We're excited to have you on board! Please choose one of the following options:</p>
                        <div>
                            <a href="{accept_new_user_url}" class="button">Accept Invitation and Create Account</a>
                            <a href="{accept_signin_url}" class="button">Accept Invitation and Sign In</a>
                        </div>
                        <p>If you don't want to join this organization, you can reject the invitation:</p>
                        <a href="{reject_url}" class="button reject-button">Reject Invitation</a>
                        <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                        <p>Best regards,<br>The {organization_name} Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            body = f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Password Reset</title>
                            <style>
                                body {{
                                    font-family: Arial, sans-serif;
                                    line-height: 1.6;
                                    color: #E6E6E6;
                                    background-color: #1C1C1C;
                                    margin: 0;
                                    padding: 20px;
                                }}
                                .container {{
                                    max-width: 600px;
                                    margin: 0 auto;
                                }}
                                .header {{
                                    background-color: #1d9a78;
                                    padding: 20px;
                                    border-radius: 5px;
                                    position: relative;
                                }}
                                .header-content {{
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    position: relative;
                                    max-width: 80%;
                                    margin: 0 auto;
                                }}
                                .header h1 {{
                                    color: white;
                                    font-size: 24px;
                                    margin: 0;
                                }}
                                .logo {{
                                    width: 80px;
                                    height: auto;
                                    margin-left: 20px;
                                }}
                                .content {{
                                    padding: 20px 0;
                                }}
                                p {{
                                    margin: 16px 0;
                                    font-size: 16px;
                                }}
                                .button {{
                                    display: inline-block;
                                    background-color: #1d9a78;
                                    color: white;
                                    text-decoration: none;
                                    padding: 10px 20px;
                                    border-radius: 5px;
                                    margin-top: 10px;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <div class="header-content">
                                        <h1>Password Reset</h1>
                                        <img src="{LOGO_URL}" alt="Company Logo" class="logo">
                                    </div>
                                </div>
                                <div class="content">
                                    <p>Dear User,</p>
                                    <p>You have requested to reset your password. Click the button below to set a new password:</p>
                                    <a href="{password_reset_url}" class="button">Reset Password</a>
                                    <p>If you didn't request a password reset, please ignore this email or contact our support team if you have any concerns.</p>
                                    <p>Best regards,<br>The Support Team</p>
                                </div>
                            </div>
                        </body>
                        </html>
                        """

        return EmailContent(subject=subject, body=body, is_html=is_html, to_email=template_vars.user.email)

    original_implementation.get_content = get_content
    return original_implementation


def override_email_password_apis(original_implementation: APIInterface):
    """Extends the sign-up process to include first name and last name'"""

    from supertokens_python.recipe.usermetadata.asyncio import update_user_metadata

    original_sign_up_post = original_implementation.sign_up_post

    async def sign_up_post(
        form_fields: List[FormField], tenant_id, api_options: APIOptions, user_context: Dict[str, Any]
    ):
        response = await original_sign_up_post(form_fields, tenant_id, api_options, user_context)

        if isinstance(response, SignUpPostOkResult):
            first_name = next(f.value for f in form_fields if f.id == "firstName")
            last_name = next(f.value for f in form_fields if f.id == "lastName")

            await update_user_metadata(response.user.user_id, {"first_name": first_name, "last_name": last_name})

        return response

    original_implementation.sign_up_post = sign_up_post
    return original_implementation


def functions_override(original_impl: RecipeInterface):
    og_emailpassword_sign_in = original_impl.sign_in
    og_update_email_or_password = original_impl.update_email_or_password
    og_reset_password_using_token = original_impl.reset_password_using_token

    # Prevents using the fake password (Initially assigned to invited users)
    async def update_email_or_password(
        user_id: str,
        email: Union[str, None],
        password: Union[str, None],
        apply_password_policy: Union[bool, None],
        tenant_id_for_password_policy: str,
        user_context: Dict[str, Any],
    ):
        if password == FAKE_PASSWORD:
            raise Exception("Please use a different password")

        return await og_update_email_or_password(
            user_id, email, password, apply_password_policy, tenant_id_for_password_policy, user_context
        )

    # Handles password reset and assigns users to organizations
    async def reset_password_using_token(
        token: str, new_password: str, tenant_id: str, user_context: Dict[str, Any]
    ) -> Union[ResetPasswordUsingTokenOkResult, ResetPasswordUsingTokenInvalidTokenError]:
        if new_password == FAKE_PASSWORD:
            return ResetPasswordUsingTokenInvalidTokenError()

        result = await og_reset_password_using_token(token, new_password, tenant_id, user_context)

        if isinstance(result, ResetPasswordUsingTokenOkResult):
            user_id = user_context.get("user_id")
            if not user_id:
                user = await get_user_by_id(result.user_id)
                if user:
                    user_id = user.user_id
            if user_id:
                user_metadata = await get_user_metadata(user_id)
                pending_org_id = user_metadata.metadata.get("pending_org_id")
                if pending_org_id:
                    await update_user_metadata(
                        user_id,
                        {
                            "organization_id": pending_org_id,
                        },
                    )
        return result

    # Prevents signing in with Fake password (User must change the password before signing in)
    async def emailpassword_sign_in(
        email: str, password: str, tenant_id: str, user_context: Dict[str, Any]
    ) -> Union[SignInOkResult, SignInWrongCredentialsError]:
        if password == FAKE_PASSWORD:
            return SignInWrongCredentialsError()
        return await og_emailpassword_sign_in(email, password, tenant_id, user_context)

    original_impl.update_email_or_password = update_email_or_password
    original_impl.reset_password_using_token = reset_password_using_token
    original_impl.sign_in = emailpassword_sign_in
    return original_impl


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
                override=emailpassword.InputOverrideConfig(
                    apis=override_email_password_apis, functions=functions_override
                ),
                email_delivery=EmailDeliveryConfig(
                    service=emailpassword.SMTPService(
                        smtp_settings=smtp_settings, override=custom_smtp_content_override
                    )
                ),
            ),
            emailverification.init(
                mode="OPTIONAL",
                email_delivery=EmailDeliveryConfig(service=emailverification.SMTPService(smtp_settings=smtp_settings)),
            ),
            dashboard.init(),
            userroles.init(),
            usermetadata.init(),
            jwt.init(),
        ],
        mode="asgi",
    )
