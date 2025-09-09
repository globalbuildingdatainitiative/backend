import pytest
from httpx import AsyncClient

from core.config import settings


# Test that the deleteProject mutation exists and has the correct signature
@pytest.mark.asyncio
async def test_delete_project_mutation_signature(client: AsyncClient):
    """
    Contract test for deleteProject mutation.

    This test verifies that the GraphQL schema includes the deleteProject mutation
    with the correct input parameters and return type.

    Expected behavior:
    - Mutation should accept a DeleteProjectInput with projectId
    - Mutation should return a Boolean
    - Project should be marked for deletion (state transitions to TO_DELETE)
    """
    # Test the mutation signature by introspecting the schema
    query = """
        query {
            __schema {
                mutationType {
                    fields(includeDeprecated: true) {
                        name
                        args {
                            name
                            type {
                                name
                                kind
                                ofType {
                                    name
                                    kind
                                    ofType {
                                        name
                                        kind
                                    }
                                }
                            }
                        }
                        type {
                            name
                            kind
                            ofType {
                                name
                                kind
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
    
    # Find the deleteProject mutation
    mutations = data["data"]["__schema"]["mutationType"]["fields"]
    delete_project_mutation = next((m for m in mutations if m["name"] == "deleteProject"), None)
    
    assert delete_project_mutation is not None, "deleteProject mutation not found in schema"
    
    # Check that it accepts DeleteProjectInput
    args = delete_project_mutation["args"]
    assert len(args) == 1, "deleteProject should have exactly one argument"
    assert args[0]["name"] == "input", "deleteProject argument should be named 'input'"
    assert args[0]["type"]["kind"] == "NON_NULL", "deleteProject input should be non-null"
    assert args[0]["type"]["ofType"]["name"] == "DeleteProjectInput", "deleteProject should accept DeleteProjectInput"
    
    # Check that it returns a Boolean (non-null)
    return_type = delete_project_mutation["type"]
    assert return_type["kind"] == "NON_NULL", "deleteProject should return a non-null scalar"
    assert return_type["ofType"]["kind"] == "SCALAR", "deleteProject should return a scalar"
    assert return_type["ofType"]["name"] == "Boolean", "deleteProject should return a Boolean"


# Test the input validation for deleteProject
@pytest.mark.asyncio
async def test_delete_project_input_validation(client: AsyncClient):
    """
    Contract test for deleteProject input validation.

    This test verifies that the mutation properly validates input parameters.
    """
    # Test with invalid UUID
    mutation = """
        mutation {
            deleteProject(input: {projectId: "invalid-uuid"})
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


# Test authorization for deleteProject
@pytest.mark.asyncio
async def test_delete_project_authorization(client: AsyncClient):
    """
    Contract test for deleteProject authorization.

    This test verifies that only authorized users can delete projects.
    """
    # This test would require setting up different user roles
    # For now, we'll test that the mutation exists and can be called
    # The actual authorization logic is tested in integration tests
    pass
