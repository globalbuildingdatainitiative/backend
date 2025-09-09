import logging
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import httpx
from httpx import Request
from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

from core.exceptions import MicroServiceConnectionError, MicroServiceResponseError
from logic.federation import get_auth_user, create_jwt


@pytest.mark.asyncio
async def test_valid_user_retrieval():
    """Test that valid user data is retrieved from auth service"""
    # Given
    user_id = uuid4()

    mock_response_data = {"data": {"users": {"items": [{"id": str(user_id), "organizationId": str(uuid4())}]}}}

    # When
    with patch("logic.federation.create_jwt", return_value="mock_jwt"), patch("httpx.AsyncClient") as mock_client:
        # Mock the HTTP client response
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=AsyncMock(is_error=False, json=lambda: mock_response_data))

        result = await get_auth_user(user_id)

        # Then
        assert result["id"] == str(user_id)
        assert "organizationId" in result


@pytest.mark.asyncio
async def test_missing_user_error_handling(caplog):
    """Test that missing user data is handled with appropriate error"""
    # Given
    user_id = uuid4()

    mock_response_data = {
        "data": {
            "users": {
                "items": []  # Empty items list
            }
        }
    }

    # Capture logs at error level
    with caplog.at_level(logging.ERROR):
        # When / Then
        with patch("logic.federation.create_jwt", return_value="mock_jwt"), patch("httpx.AsyncClient") as mock_client:
            # Mock the HTTP client response
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.post = AsyncMock(return_value=AsyncMock(is_error=False, json=lambda: mock_response_data))

            with pytest.raises(MicroServiceResponseError):
                await get_auth_user(user_id)

            # Then
            assert f"No user found in auth service for uid: {user_id}" in caplog.text


@pytest.mark.asyncio
async def test_http_request_error():
    """Test that HTTP request errors are handled properly"""
    # Given
    user_id = uuid4()

    # When / Then
    with patch("logic.federation.create_jwt", return_value="mock_jwt"), patch("httpx.AsyncClient") as mock_client:
        # Mock the HTTP client to raise a RequestError
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_request = Request("POST", "http://example.com")
        mock_instance.post = AsyncMock(side_effect=httpx.RequestError("Connection failed", request=mock_request))

        with pytest.raises(MicroServiceConnectionError):
            await get_auth_user(user_id)


@pytest.mark.asyncio
async def test_http_error_response():
    """Test that HTTP error responses are handled properly"""
    # Given
    user_id = uuid4()

    # When / Then
    with patch("logic.federation.create_jwt", return_value="mock_jwt"), patch("httpx.AsyncClient") as mock_client:
        # Mock the HTTP client to return an error response
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_response = AsyncMock()
        mock_response.is_error = True
        mock_response.text = "Internal Server Error"
        mock_instance.post = AsyncMock(return_value=mock_response)

        with pytest.raises(MicroServiceConnectionError):
            await get_auth_user(user_id)


@pytest.mark.asyncio
async def test_graphql_errors_in_response(caplog):
    """Test that GraphQL errors in response are handled properly"""
    # Given
    user_id = uuid4()

    mock_response_data = {"data": None, "errors": [{"message": "User not found", "path": ["users", "items", 0]}]}

    # Capture logs at error level
    with caplog.at_level(logging.ERROR):
        # When / Then
        with patch("logic.federation.create_jwt", return_value="mock_jwt"), patch("httpx.AsyncClient") as mock_client:
            # Mock the HTTP client response with GraphQL errors
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.post = AsyncMock(return_value=AsyncMock(is_error=False, json=lambda: mock_response_data))

            with pytest.raises(MicroServiceResponseError):
                await get_auth_user(user_id)

            # Then
            assert f"GraphQL errors in get_auth_user for user {user_id}" in caplog.text


@pytest.mark.asyncio
async def test_create_jwt_success():
    """Test that JWT creation works correctly"""
    # Given
    mock_jwt_result = CreateJwtOkResult(jwt="test_jwt_token")

    # When
    with patch("supertokens_python.recipe.jwt.asyncio.create_jwt", return_value=mock_jwt_result):
        result = await create_jwt()

        # Then
        assert result == "test_jwt_token"


@pytest.mark.asyncio
async def test_create_jwt_failure():
    """Test that JWT creation failure is handled correctly"""
    # Given
    mock_jwt_result = "failure"  # Not a CreateJwtOkResult

    # When / Then
    with patch("supertokens_python.recipe.jwt.asyncio.create_jwt", return_value=mock_jwt_result):
        with pytest.raises(Exception) as exc_info:
            await create_jwt()

        # Then
        assert "Unable to create JWT. Should never come here." in str(exc_info.value)
