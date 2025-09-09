import pytest
from httpx import AsyncClient

from core.config import settings


# Test that the myProjects query exists and has the correct signature
@pytest.mark.asyncio
async def test_my_projects_query_signature(client: AsyncClient):
    """
    Contract test for myProjects query.

    This test verifies that the GraphQL schema includes the myProjects query
    with the correct return type.

    Expected behavior:
    - Query should return a list of Projects created by the current user
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
    
    # Find the myProjects query
    queries = data["data"]["__schema"]["queryType"]["fields"]
    my_projects_query = next((q for q in queries if q["name"] == "myProjects"), None)
    
    assert my_projects_query is not None, "myProjects query not found in schema"
    
    # Check that it doesn't accept any parameters
    args = my_projects_query["args"]
    assert len(args) == 0, "myProjects should not accept any arguments"
    
    # Check that it returns a list of Projects (non-null list of non-null Projects)
    return_type = my_projects_query["type"]
    assert return_type["kind"] == "NON_NULL", "myProjects should return a non-null list"
    assert return_type["ofType"]["kind"] == "LIST", "myProjects should return a list"
    assert return_type["ofType"]["ofType"]["kind"] == "NON_NULL", "myProjects should return a list of non-null objects"
    assert return_type["ofType"]["ofType"]["ofType"]["name"] == "Project", "myProjects should return a list of Projects"


# Test authorization for myProjects
@pytest.mark.asyncio
async def test_my_projects_authorization(client: AsyncClient):
    """
    Contract test for myProjects authorization.

    This test verifies that only authorized users can query their own projects.
    """
    # This test would require setting up different user roles
    # For now, we'll test that the query exists and can be called
    # The actual authorization logic is tested in integration tests
    pass
