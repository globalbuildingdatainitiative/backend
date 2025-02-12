import pytest
from uuid import uuid4

from core.auth import (
    generate_invitation_email_new_user,
    generate_invitation_email_existing_user,
    generate_password_reset_email,
)


@pytest.mark.asyncio
async def test_generate_invitation_email_new_user():
    """Test generating invitation email for new users"""
    organization_name = "Test Org"
    inviter_name = "John Doe"
    user_id = str(uuid4())
    origin = "http://localhost:3000"

    subject, body = await generate_invitation_email_new_user(organization_name, inviter_name, user_id, origin)

    # Check subject
    assert subject == f"Invitation to join {organization_name}"

    # Check body contains key elements
    assert organization_name in body
    assert inviter_name in body
    assert user_id in body
    assert origin in body
    assert "Create Account" in body
    assert "Reject Invitation" in body
    assert "accept-invite-new" in body
    assert "reject-invite" in body


@pytest.mark.asyncio
async def test_generate_invitation_email_existing_user():
    """Test generating invitation email for existing users"""
    organization_name = "Test Org"
    inviter_name = "John Doe"
    user_id = str(uuid4())
    origin = "http://localhost:3000"

    subject, body = await generate_invitation_email_existing_user(organization_name, inviter_name, user_id, origin)

    # Check subject
    assert subject == f"Invitation to join {organization_name}"

    # Check body contains key elements
    assert organization_name in body
    assert inviter_name in body
    assert user_id in body
    assert origin in body
    assert "Sign In" in body
    assert "Reject Invitation" in body
    assert "accept-invite" in body
    assert "reject-invite" in body


@pytest.mark.asyncio
async def test_generate_password_reset_email():
    """Test generating password reset email"""
    reset_url = "http://localhost:3000/reset-password?token=abc123"

    subject, body = await generate_password_reset_email(reset_url)

    # Check subject
    assert subject == "Reset Your Password"

    # Check body contains key elements
    assert reset_url in body
    assert "Password Reset" in body
    assert "Reset Password" in body
    assert "requested to reset your password" in body
