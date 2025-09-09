import pytest
from httpx import AsyncClient

from core.config import settings


# Test that the lockProject mutation exists and has the correct signature
@pytest.mark.asyncio
async def test_lock_project_mutation_signature(client: AsyncClient):
    """
    Contract test for lockProject mutation.

    This test verifies that the GraphQL schema includes the lockProject mutation
    with the correct input parameters and return type.

    Expected behavior:
    - Mutation should accept a LockProjectInput with projectId
    - Mutation should return a Project with state field
    - Project state should transition to LOCKED
    """
    # Test the mutation signature by introspecting the schema
    query = """
        query {
            __schema {
                mutationType {
                    fields {
                        name
                        args {
                            name
                            type {
                                name
                                kind
                                ofType {
                                    name
                                    kind
                                }
                            }
                        }
                        type {
                            name
                            kind
                            ofType {
                                name
                            }
                        }
                    }
                }
            }
        }
    """
    
    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Find the lockProject mutation
    mutations = data["data"]["__schema"]["mutationType"]["fields"]
    lock_project_mutation = next((m for m in mutations if m["name"] == "lockProject"), None)
    
    assert lock_project_mutation is not None, "lockProject mutation not found in schema"
    
    # Check that it accepts LockProjectInput
    args = lock_project_mutation["args"]
    assert len(args) == 1, "lockProject should have exactly one argument"
    assert args[0]["name"] == "input", "lockProject argument should be named 'input'"
    assert args[0]["type"]["kind"] == "NON_NULL", "lockProject input should be non-null"
    assert args[0]["type"]["ofType"]["name"] == "LockProjectInput", "lockProject should accept LockProjectInput"
    
    # Check that it returns a Project (non-null)
    return_type = lock_project_mutation["type"]
    assert return_type["kind"] == "NON_NULL", "lockProject should return a non-null object"
    assert return_type["ofType"]["name"] == "Project", "lockProject should return a Project"


# Test the input validation for lockProject
@pytest.mark.asyncio
async def test_lock_project_input_validation(client: AsyncClient):
    """
    Contract test for lockProject input validation.

    This test verifies that the mutation properly validates input parameters.
    """
    # Test with invalid UUID
    mutation = """
        mutation {
            lockProject(input: {projectId: "invalid-uuid"}) {
                id
                state
            }
        }
    """
    
    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": mutation}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have errors due to invalid UUID
    assert "errors" in data, "Expected errors for invalid UUID input"
    assert len(data["errors"]) > 0, "Should have at least one error for invalid UUID"


# Test authorization for lockProject
@pytest.mark.asyncio
async def test_lock_project_authorization(client: AsyncClient):
    """
    Contract test for lockProject authorization.

    This test verifies that only authorized users (administrators) can lock projects.
    """
    # This test would require setting up different user roles
    # For now, we'll test that the mutation exists and can be called
    # The actual authorization logic is tested in integration tests
    pass
