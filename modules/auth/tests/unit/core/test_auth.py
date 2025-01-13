from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from supertokens_python.recipe.emailpassword.types import PasswordResetEmailTemplateVars
from supertokens_python.ingredients.emaildelivery.types import EmailContent
from core.auth import custom_smtp_content_override


@pytest.mark.asyncio
@patch("core.auth.generate_password_reset_email")
@patch("supertokens_python.recipe.usermetadata.asyncio.get_user_metadata")
async def test_reset_password_email(
    mock_get_user_metadata,
    mock_generate_password_reset_email,
    app,
):
    """
    Test that if inviter_id and pending_org_id are NOT set in user metadata,
    the code should generate a reset password email.
    """

    # 1) Setup user metadata (simulate no invitation data => reset password scenario)
    mock_get_user_metadata.return_value = MagicMock(
        metadata={
            "first_name": "",
            "last_name": "",
            "invited": False,
            "invite_status": "none",
            "inviter_name": "",
        }
    )

    # 2) Mock the generate_password_reset_email to return a known subject/body
    mock_generate_password_reset_email.return_value = (
        "Reset Password Subject",
        "<p>Reset Password Body</p>",
    )

    # 3) Create template vars for reset password
    template_vars = PasswordResetEmailTemplateVars(
        user=MagicMock(id="test-user-id", email="test@example.com"),
        password_reset_link="http://test.reset.link",
        tenant_id="public",
    )

    override_impl = custom_smtp_content_override(AsyncMock())
    get_content_fn = override_impl.get_content

    result: EmailContent = await get_content_fn(template_vars, user_context={})

    mock_generate_password_reset_email.assert_awaited_once_with("http://test.reset.link")

    # 7) Check the returned EmailContent
    assert result.subject == "Reset Password Subject"
    assert result.body == "<p>Reset Password Body</p>"
    assert result.is_html is True
    assert result.to_email == "test@example.com"


@pytest.mark.asyncio
@patch("logic.get_organization_name")
@patch("supertokens_python.recipe.usermetadata.asyncio.get_user_metadata")
async def test_existing_user_invitation_email(
    mock_get_user_metadata,
    mock_get_organization_name,
    app,
):
    """
    Test that when user metadata contains invitation data and user exists (has name),
    the code should generate an invitation email for existing user.
    """

    # 1) Setup user metadata for existing user with invitation data
    inviter_id = str(uuid4())
    org_id = str(uuid4())
    mock_get_user_metadata.side_effect = [
        # First call for user metadata
        MagicMock(
            metadata={"first_name": "John", "last_name": "Doe", "inviter_id": inviter_id, "pending_org_id": org_id}
        ),
        # Second call for inviter metadata
        MagicMock(metadata={"first_name": "Jane", "last_name": "Smith"}),
    ]

    # 2) Mock organization name
    mock_get_organization_name.return_value = "Test Organization"

    template_vars = PasswordResetEmailTemplateVars(
        user=MagicMock(id="existing-user-id", email="test@example.com"),
        password_reset_link="http://test.reset.link",
        tenant_id="public",
    )

    override_impl = custom_smtp_content_override(AsyncMock())
    get_content_fn = override_impl.get_content

    result: EmailContent = await get_content_fn(template_vars, user_context={})

    assert result.subject == "Invitation to join Test Organization"
    assert result.is_html is True
    assert result.to_email == "test@example.com"
    assert "Accept Invitation and Sign In" in result.body
    assert "/accept-invite?" in result.body
    assert "Jane Smith" in result.body
    assert "Test Organization" in result.body


@pytest.mark.asyncio
@patch("logic.get_organization_name")
@patch("supertokens_python.recipe.usermetadata.asyncio.get_user_metadata")
async def test_new_user_invitation_email(
    mock_get_user_metadata,
    mock_get_organization_name,
    app,
):
    """
    Test that when user metadata contains invitation data but user doesn't exist (no name),
    the code should generate an invitation email for new user.
    """

    # 1) Setup user metadata for new user with invitation data
    inviter_id = str(uuid4())
    org_id = str(uuid4())
    mock_get_user_metadata.side_effect = [
        # First call for user metadata (new user, no names)
        MagicMock(metadata={"inviter_id": inviter_id, "pending_org_id": org_id}),
        # Second call for inviter metadata
        MagicMock(metadata={"first_name": "Jane", "last_name": "Smith"}),
    ]

    # 2) Mock organization name
    mock_get_organization_name.return_value = "Test Organization"

    # 4) Create template vars
    template_vars = PasswordResetEmailTemplateVars(
        user=MagicMock(id="new-user-id", email="newuser@example.com"),
        password_reset_link="http://test.reset.link",
        tenant_id="public",
    )

    # 5) Call the custom_smtp_content_override
    override_impl = custom_smtp_content_override(AsyncMock())
    get_content_fn = override_impl.get_content

    # 6) Get the result
    result: EmailContent = await get_content_fn(template_vars, user_context={})

    # 7) Verify calls and result
    assert result.subject == "Invitation to join Test Organization"
    assert result.is_html is True
    assert result.to_email == "newuser@example.com"
    assert "Accept Invitation and Create Account" in result.body
    assert "/accept-invite-new?" in result.body
    assert "Jane Smith" in result.body
    assert "Test Organization" in result.body
