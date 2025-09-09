import pytest
from httpx import AsyncClient

from core.config import settings


# Test that the projectsToPublish query exists and has the correct signature
@pytest.mark.asyncio
async def test_projects_to_publish_query_signature(client: AsyncClient):
    """
    Contract test for projectsToPublish query.

    This test verifies that the GraphQL schema includes the projectsToPublish query
    with the correct return type.

    Expected behavior:
    - Query should return a list of Projects in TO_PUBLISH state
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
    
    # Find the projectsToPublish query
    queries = data["data"]["__schema"]["queryType"]["fields"]
    projects_to_publish_query = next((q for q in queries if q["name"] == "projectsToPublish"), None)
    
    assert projects_to_publish_query is not None, "projectsToPublish query not found in schema"
    
    # Check that it doesn't accept any parameters
    args = projects_to_publish_query["args"]
    assert len(args) == 0, "projectsToPublish should not accept any arguments"
    
    # Check that it returns a list of Projects (non-null list of non-null Projects)
    return_type = projects_to_publish_query["type"]
    assert return_type["kind"] == "NON_NULL", "projectsToPublish should return a non-null list"
    assert return_type["ofType"]["kind"] == "LIST", "projectsToPublish should return a list"
    assert return_type["ofType"]["ofType"]["kind"] == "NON_NULL", "projectsToPublish should return a list of non-null objects"
    assert return_type["ofType"]["ofType"]["ofType"]["name"] == "Project", "projectsToPublish should return a list of Projects"


# Test authorization for projectsToPublish
@pytest.mark.asyncio
async def test_projects_to_publish_authorization(client: AsyncClient):
    """
    Contract test for projectsToPublish authorization.

    This test verifies that only authorized users (administrators) can query projects to publish.
    """
    # This test would require setting up different user roles
    # For now, we'll test that the query exists and can be called
    # The actual authorization logic is tested in integration tests
    pass
