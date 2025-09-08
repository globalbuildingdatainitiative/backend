# Contract Tests: User-Organization Relationship Management

## Overview
Contract tests validate that the implementation meets the specification requirements. These tests are written before implementation and drive the development process.

## Test Environment Setup
```bash
# Set up test environment
pip install pytest pytest-asyncio httpx moto[all] pytest-cov
```

## Test Suite 1: Organization Creation Contract Tests

### Test 1.1: Valid Organization Creation
```python
import pytest
from uuid import UUID
from backend.modules.organization.src.logic.organization import create_organizations_mutation
from backend.modules.organization.src.models.organization import InputOrganization, InputOrganizationMetaData

@pytest.mark.asyncio
async def test_valid_organization_creation():
    """Test that valid organization data creates an organization successfully"""
    # Given
    organization_data = InputOrganization(
        name="Test Organization",
        address="123 Test Street",
        city="Test City",
        country="CHE",  # Switzerland
        meta_data=InputOrganizationMetaData(stakeholders=[])
    )
    
    current_user = SuperTokensUser(id=UUID("12345678-1234-5678-1234-567812345678"), organization_id=None)
    
    # When
    result = await create_organizations_mutation([organization_data], current_user)
    
    # Then
    assert len(result) == 1
    assert result[0].name == "Test Organization"
    assert result[0].address == "123 Test Street"
    assert result[0].city == "Test City"
    assert result[0].country == "CHE"
    assert isinstance(result[0].id, UUID)
```

### Test 1.2: Organization Creation with Verification
```python
import pytest
from unittest.mock import patch, AsyncMock
from uuid import UUID
from backend.modules.organization.src.logic.organization import create_organizations_mutation
from backend.modules.organization.src.models.organization import DBOrganization, InputOrganization, InputOrganizationMetaData

@pytest.mark.asyncio
async def test_organization_creation_verification():
    """Test that organization creation includes verification step"""
    # Given
    organization_data = InputOrganization(
        name="Test Organization",
        address="123 Test Street",
        city="Test City",
        country="CHE",
        meta_data=InputOrganizationMetaData(stakeholders=[])
    )
    
    current_user = SuperTokensUser(id=UUID("12345678-1234-5678-1234-567812345678"), organization_id=None)
    
    # Mock the verification step
    with patch('backend.modules.organization.src.models.organization.DBOrganization.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = AsyncMock()  # Return a mock organization
        
        # When
        result = await create_organizations_mutation([organization_data], current_user)
        
        # Then
        assert len(result) == 1
        # Verify that the get method was called for verification
        mock_get.assert_called_once_with(result[0].id)
```

## Test Suite 2: User-Organization Resolution Contract Tests

### Test 2.1: Successful Organization Resolution
```python
import pytest
from unittest.mock import patch, AsyncMock
from uuid import UUID
from backend.modules.organization.src.models.user import GraphQLUser, get_user_organization
from backend.modules.organization.src.models.organization import GraphQLOrganization

@pytest.mark.asyncio
async def test_successful_organization_resolution():
    """Test that user with valid organization ID resolves organization correctly"""
    # Given
    user = GraphQLUser(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        organizationId=UUID("87654321-4321-8765-4321-876543218765")
    )
    
    expected_organization = GraphQLOrganization(
        id=UUID("87654321-4321-8765-4321-876543218765"),
        name="Test Organization",
        address="123 Test Street",
        city="Test City",
        country="CHE",
        meta_data=OrganizationMetaData(stakeholders=[])
    )
    
    # Mock the get_organizations function
    with patch('backend.modules.organization.src.models.user.get_organizations', new_callable=AsyncMock) as mock_get_orgs:
        mock_get_orgs.return_value = [expected_organization]
        
        # When
        result = await get_user_organization(user)
        
        # Then
        assert result is not None
        assert result.id == expected_organization.id
        assert result.name == "Test Organization"
```

### Test 2.2: Missing Organization Resolution
```python
import pytest
from unittest.mock import patch, AsyncMock
import logging
from uuid import UUID
from backend.modules.organization.src.models.user import GraphQLUser, get_user_organization

@pytest.mark.asyncio
async def test_missing_organization_resolution(caplog):
    """Test that user with missing organization ID returns None and logs warning"""
    # Given
    user = GraphQLUser(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        organizationId=UUID("87654321-4321-8765-4321-876543218765")
    )
    
    # Capture logs
    with caplog.at_level(logging.WARNING):
        # Mock the get_organizations function to return empty list
        with patch('backend.modules.organization.src.models.user.get_organizations', new_callable=AsyncMock) as mock_get_orgs:
            mock_get_orgs.return_value = []
            
            # When
            result = await get_user_organization(user)
            
            # Then
            assert result is None
            assert "No organization found for user" in caplog.text
```

## Test Suite 3: Federation Error Handling Contract Tests

### Test 3.1: Valid User Retrieval
```python
import pytest
from unittest.mock import patch, AsyncMock
import httpx
from uuid import UUID
from backend.modules.organization.src.logic.federation import get_auth_user

@pytest.mark.asyncio
async def test_valid_user_retrieval():
    """Test that valid user data is retrieved from auth service"""
    # Given
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    mock_response_data = {
        "data": {
            "users": {
                "items": [{
                    "id": "12345678-1234-5678-1234-567812345678",
                    "organizationId": "87654321-4321-8765-4321-876543218765"
                }]
            }
        }
    }
    
    # Mock the HTTP client
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=AsyncMock(
            is_error=False,
            json=lambda: mock_response_data
        ))
        
        # When
        result = await get_auth_user(user_id)
        
        # Then
        assert result["id"] == "12345678-1234-5678-1234-567812345678"
        assert result["organizationId"] == "87654321-4321-8765-4321-876543218765"
```

### Test 3.2: Missing User Error Handling
```python
import pytest
from unittest.mock import patch, AsyncMock
import httpx
from uuid import UUID
from backend.modules.organization.src.logic.federation import get_auth_user
from backend.modules.organization.src.core.exceptions import MicroServiceResponseError

@pytest.mark.asyncio
async def test_missing_user_error_handling():
    """Test that missing user data is handled with appropriate error"""
    # Given
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    mock_response_data = {
        "data": {
            "users": {
                "items": []  # Empty items list
            }
        }
    }
    
    # Mock the HTTP client
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock(return_value=AsyncMock(
            is_error=False,
            json=lambda: mock_response_data
        ))
        
        # When / Then
        with pytest.raises(MicroServiceResponseError):
            await get_auth_user(user_id)
```

## Test Suite 4: GraphQL Query Contract Tests

### Test 4.1: Get Current User Query Structure
```python
import pytest
from graphql import build_schema

def test_get_current_user_query_structure():
    """Test that the GraphQL query has the correct structure"""
    # Given
    schema_sdl = """
    type Query {
        users: UserGraphQLResponse!
    }
    
    type UserGraphQLResponse {
        items(filterBy: FilterBy, sortBy: SortBy, offset: Int!, limit: Int): [User!]
        count(filterBy: FilterBy): Int!
    }
    
    input FilterBy {
        equal: JSON
        contains: JSON
    }
    
    input SortBy {
        asc: String
        dsc: String
    }
    
    scalar JSON
    
    type User {
        id: UUID!
        firstName: String
        lastName: String
        email: String!
        roles: [Role!]
        organization: Organization
        timeJoined: DateTime!
    }
    
    type Organization {
        id: UUID!
        name: String!
        address: String!
        city: String!
        country: CountryCodes!
        metaData: OrganizationMetaData!
    }
    
    enum Role {
        OWNER
        MEMBER
        ADMIN
    }
    
    enum CountryCodes {
        CHE
        USA
        DEU
    }
    
    type OrganizationMetaData {
        stakeholders: [StakeholderEnum!]!
    }
    
    enum StakeholderEnum {
        BUILDING_DATA_OWNERS
        DESIGN_PROFESSIONALS
    }
    
    scalar UUID
    scalar DateTime
    """
    
    # When
    schema = build_schema(schema_sdl)
    
    # Then
    # Verify schema has required types
    assert "Query" in schema.type_map
    assert "User" in schema.type_map
    assert "Organization" in schema.type_map
    assert "users" in schema.query_type.fields
```

### Test 4.2: Query Variables Validation
```python
import pytest
from graphql import parse, validate, build_schema

def test_get_current_user_query_variables():
    """Test that the GraphQL query accepts correct variables"""
    # Given
    schema_sdl = """
    type Query {
        users: UserGraphQLResponse!
    }
    
    type UserGraphQLResponse {
        items(filterBy: FilterBy, sortBy: SortBy, offset: Int!, limit: Int): [User!]
        count(filterBy: FilterBy): Int!
    }
    
    input FilterBy {
        equal: JSON
    }
    
    scalar JSON
    
    type User {
        id: UUID!
        organization: Organization
    }
    
    type Organization {
        id: UUID!
    }
    
    scalar UUID
    """
    
    query_string = """
    query getCurrentUser($id: String!) {
        users {
            items(filterBy: { equal: { id: $id } }, limit: 1) {
                id
                organization {
                    id
                }
            }
        }
    }
    """
    
    schema = build_schema(schema_sdl)
    ast = parse(query_string)
    
    # When
    errors = validate(schema, ast)
    
    # Then
    assert len(errors) == 0, f"Query validation failed: {errors}"
```

## Execution Instructions

### Running Contract Tests
```bash
# Run all contract tests
pytest docs/001-user-org-relationship/implementation-details/06-contract-tests.md -v

# Run specific test suite
pytest docs/001-user-org-relationship/implementation-details/06-contract-tests.md::test_valid_organization_creation -v

# Run with coverage
pytest docs/001-user-org-relationship/implementation-details/06-contract-tests.md --cov=backend/modules/organization/src --cov-report=html
```

## Test Validation Criteria

### Success Criteria
1. All contract tests pass with no failures
2. Test coverage for relationship management code is >90%
3. No race conditions detected in concurrent execution
4. Error handling paths are fully tested

### Failure Conditions
1. Any contract test failure indicates implementation does not meet specification
2. Missing test coverage on critical paths requires implementation revision
3. Performance degradation in test environment requires optimization
4. Race conditions in tests require synchronization improvements

## Maintenance
Contract tests should be updated when:
1. Specification requirements change
2. New error conditions are identified
3. Performance requirements are modified
4. API contracts are extended

Contract tests should NOT be updated when:
1. Implementation details change but behavior remains the same
2. Refactoring occurs without functional changes
3. Performance optimizations are made
4. Logging or monitoring is enhanced
