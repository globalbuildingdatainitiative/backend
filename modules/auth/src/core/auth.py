import logging
from typing import List, Dict, Any, Union
from uuid import UUID

import httpx
from supertokens_python import init, InputAppInfo, SupertokensConfig, RecipeUserId
from supertokens_python.framework.request import BaseRequest
from supertokens_python.ingredients.emaildelivery.types import (
    EmailDeliveryConfig,
    SMTPSettings,
    SMTPSettingsFrom,
    EmailContent,
)
from supertokens_python.recipe import session, userroles, usermetadata, emailpassword, dashboard, jwt, emailverification
from supertokens_python.recipe.emailpassword import InputFormField
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface,
    APIOptions,
    SignUpPostOkResult,
    RecipeInterface,
    SignInOkResult,
    WrongCredentialsError,
)
from supertokens_python.recipe.emailpassword.types import FormField, PasswordResetEmailTemplateVars, SMTPOverrideInput
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.recipe.usermetadata.asyncio import get_user_metadata
from tenacity import stop_after_attempt, wait_fixed, before_log, after_log, retry

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
            elif origin.endswith("epfl.ch"):
                return origin
            elif origin.startswith("http://localhost"):
                return origin

    logger.debug(f"Origin not found in request. Using default origin {settings.BACKEND_CORS_ORIGINS[0]}")
    return settings.BACKEND_CORS_ORIGINS[0]


# SMTP Configuration
def get_smtp_settings():
    return SMTPSettings(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        from_=SMTPSettingsFrom(name=settings.SMTP_NAME, email=settings.SMTP_EMAIL),
        password=settings.SMTP_PASSWORD,
        secure=False,
        username=settings.SMTP_USERNAME,
    )


def get_base_email_style() -> str:
    return """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #E6E6E6;
            background-color: #1C1C1C;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            background-color: #1d9a78;
            padding: 20px;
            border-radius: 5px;
            position: relative;
        }
        .header-content {
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            max-width: 80%;
            margin: 0 auto;
        }
        .header h1 {
            color: white;
            font-size: 24px;
            margin: 0;
        }
        .logo {
            width: 80px;
            height: auto;
            margin-left: 20px;
        }
        .content {
            padding: 20px 0;
        }
        p {
            margin: 16px 0;
            font-size: 16px;
        }
        .button {
            display: inline-block;
            background-color: #1d9a78;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            margin-right: 10px;
            margin-top: 10px;
        }
        .reject-button {
            background-color: #cc4125;
        }
    """


async def generate_invitation_email_new_user(
    organization_name: str, inviter_name: str, user_id: str, origin: str
) -> tuple[str, str]:
    """Generate invitation email for new users who don't have an account yet."""
    accept_new_user_url = f"{origin}/accept-invite-new?user_id={user_id}"
    reject_url = f"{origin}/reject-invite?user_id={user_id}"

    subject = f"Invitation to join {organization_name}"
    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>
            {get_base_email_style()}
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
                <p>We're excited to have you on board! Click below to create your account:</p>
                <div>
                    <a href="{accept_new_user_url}" class="button">Accept Invitation and Create Account</a>
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
    return subject, body


async def generate_invitation_email_existing_user(
    organization_name: str, inviter_name: str, user_id: str, origin: str
) -> tuple[str, str]:
    """Generate invitation email for existing users who already have an account."""
    accept_signin_url = f"{origin}/accept-invite?user_id={user_id}"
    reject_url = f"{origin}/reject-invite?user_id={user_id}"

    subject = f"Invitation to join {organization_name}"
    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>
            {get_base_email_style()}
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
                <p>We're excited to have you on board! Click below to sign in and accept the invitation:</p>
                <div>
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
    return subject, body


async def generate_password_reset_email(password_reset_url: str) -> tuple[str, str]:
    """Generate password reset email."""
    subject = "Reset Your Password"
    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>
            {get_base_email_style()}
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
    return subject, body


def custom_smtp_content_override(original_implementation: SMTPOverrideInput) -> SMTPOverrideInput:
    """Overrides email content for password reset emails"""

    async def get_content(template_vars: PasswordResetEmailTemplateVars, user_context: Dict[str, Any]) -> EmailContent:
        from logic import get_organization_name

        user_id = template_vars.user.id
        user_metadata = await get_user_metadata(user_id)
        inviter_id = user_metadata.metadata.get("inviter_id")
        organization_id = user_metadata.metadata.get("pending_org_id")
        origin = get_origin(None, user_context)

        subject = ""
        body = ""

        # Handle invitation emails
        if inviter_id and organization_id:
            inviter_metadata = await get_user_metadata(inviter_id)
            inviter_name = f"{inviter_metadata.metadata.get('first_name', '')} {inviter_metadata.metadata.get('last_name', '')}".strip()
            organization_name = await get_organization_name(UUID(organization_id))

            # Check if user exists (has metadata)
            user_exists = bool(user_metadata.metadata.get("first_name") or user_metadata.metadata.get("last_name"))

            if user_exists:
                subject, body = await generate_invitation_email_existing_user(
                    organization_name, inviter_name, user_id, origin
                )
            else:
                subject, body = await generate_invitation_email_new_user(
                    organization_name, inviter_name, user_id, origin
                )
        # Handle password reset emails
        else:
            subject, body = await generate_password_reset_email(template_vars.password_reset_link)

        return EmailContent(subject=subject, body=body, is_html=True, to_email=template_vars.user.email)

    original_implementation.get_content = get_content
    return original_implementation


def override_email_password_apis(original_implementation: APIInterface):
    """Extends the sign-up process to include first name and last name"""
    from logic.user import create_user_meta_data

    original_sign_up_post = original_implementation.sign_up_post

    async def sign_up_post(
        form_fields: List[FormField],
        tenant_id: str,
        session: Union[SessionContainer, None],
        should_try_linking_with_session_user: Union[bool, None],
        api_options: APIOptions,
        user_context: Dict[str, Any],
    ):
        response = await original_sign_up_post(
            form_fields,
            tenant_id,
            session,
            should_try_linking_with_session_user,
            api_options,
            user_context,
        )

        if isinstance(response, SignUpPostOkResult):
            first_name = next(f.value for f in form_fields if f.id == "firstName")
            last_name = next(f.value for f in form_fields if f.id == "lastName")

            await create_user_meta_data(
                response.user.id,
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": str(response.user.emails[0]),
                    "time_joined": response.user.time_joined,
                },
            )
        return response

    original_implementation.sign_up_post = sign_up_post
    return original_implementation


def functions_override(original_impl: RecipeInterface):
    og_emailpassword_sign_in = original_impl.sign_in
    og_update_email_or_password = original_impl.update_email_or_password

    # Prevents using the fake password (Initially assigned to invited users)
    async def update_email_or_password(
        user_id: RecipeUserId,
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

    # Prevents signing in with Fake password (User must change the password before signing in)
    async def emailpassword_sign_in(
        email: str,
        password: str,
        tenant_id: str,
        session: SessionContainer | None,
        should_try_linking_with_session_user: bool | None,
        user_context: Dict[str, Any],
    ) -> Union[SignInOkResult, WrongCredentialsError]:
        if password == FAKE_PASSWORD:
            return WrongCredentialsError()
        return await og_emailpassword_sign_in(
            email, password, tenant_id, session, should_try_linking_with_session_user, user_context
        )

    original_impl.update_email_or_password = update_email_or_password
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
                        smtp_settings=get_smtp_settings(), override=custom_smtp_content_override
                    )
                ),
            ),
            emailverification.init(
                mode="OPTIONAL",
                email_delivery=EmailDeliveryConfig(
                    service=emailverification.SMTPService(smtp_settings=get_smtp_settings())
                ),
            ),
            dashboard.init(),
            userroles.init(),
            usermetadata.init(),
            jwt.init(),
        ],
        mode="asgi",
    )


@retry(
    stop=stop_after_attempt(60 * 5),
    wait=wait_fixed(1),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def health_check_supertokens():
    response = httpx.get(f"{settings.CONNECTION_URI}/hello")
    if response.status_code == 200 and response.text.strip() == "Hello":
        return True
