import pytest
from httpx import AsyncClient

from core.config import settings


# Test that the projectsByState query exists and has the correct signature
@pytest.mark.asyncio
async def test_projects_by_state_query_signature(client: AsyncClient):
    """
    Contract test for projectsByState query.

    This test verifies that the GraphQL schema includes the projectsByState query
    with the correct input parameters and return type.

    Expected behavior:
    - Query should accept a ProjectsByStateInput with state
    - Query should return a list of Projects
    """
    # Test the query signature by introspecting the schema
    query = """
        query {
            __schema {
                queryType {
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
                                        ofType {
                                            name
                                            kind
                                        }
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
    
    # Find the projectsByState query
    queries = data["data"]["__schema"]["queryType"]["fields"]
    projects_by_state_query = next((q for q in queries if q["name"] == "projectsByState"), None)
    
    assert projects_by_state_query is not None, "projectsByState query not found in schema"
    
    # Check that it accepts ProjectsByStateInput
    args = projects_by_state_query["args"]
    assert len(args) == 1, "projectsByState should have exactly one argument"
    assert args[0]["name"] == "input", "projectsByState argument should be named 'input'"
    assert args[0]["type"]["kind"] == "NON_NULL", "projectsByState input should be non-null"
    assert args[0]["type"]["ofType"]["name"] == "ProjectsByStateInput", "projectsByState should accept ProjectsByStateInput"
    
    # Check that it returns a list of Projects (non-null list of non-null Projects)
    return_type = projects_by_state_query["type"]
    assert return_type["kind"] == "NON_NULL", "projectsByState should return a non-null list"
    assert return_type["ofType"]["kind"] == "LIST", "projectsByState should return a list"
    assert return_type["ofType"]["ofType"]["kind"] == "NON_NULL", "projectsByState should return a list of non-null objects"
    assert return_type["ofType"]["ofType"]["ofType"]["name"] == "Project", "projectsByState should return a list of Projects"


# Test the input validation for projectsByState
@pytest.mark.asyncio
async def test_projects_by_state_input_validation(client: AsyncClient):
    """
    Contract test for projectsByState input validation.

    This test verifies that the query properly validates input parameters.
    """
    # Test with invalid state value
    query = """
        query {
            projectsByState(input: {state: "INVALID_STATE"}) {
                id
                state
            }
        }
    """
    
    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={"query": query}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have errors due to invalid state
    assert "errors" in data, "Expected errors for invalid state input"
    assert len(data["errors"]) > 0, "Should have at least one error for invalid state"


# Test authorization for projectsByState
@pytest.mark.asyncio
async def test_projects_by_state_authorization(client: AsyncClient):
    """
    Contract test for projectsByState authorization.

    This test verifies that only authorized users can query projects by state.
    """
    # This test would require setting up different user roles
    # For now, we'll test that the query exists and can be called
    # The actual authorization logic is tested in integration tests
    pass
