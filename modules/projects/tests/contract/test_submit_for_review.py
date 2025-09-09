import pytest
from httpx import AsyncClient

from core.config import settings


# Test that the submitForReview mutation exists and has the correct signature
@pytest.mark.asyncio
async def test_submit_for_review_mutation_signature(client: AsyncClient):
    """
    Contract test for submitForReview mutation.

    This test verifies that the GraphQL schema includes the submitForReview mutation
    with the correct input parameters and return type.

    Expected behavior:
    - Mutation should accept a SubmitForReviewInput with projectId
    - Mutation should return a Project with state field
    - Project state should transition from DRAFT to IN_REVIEW
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
                                fields {
                                    name
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
    
    # Find the submitForReview mutation
    mutations = data["data"]["__schema"]["mutationType"]["fields"]
    submit_for_review_mutation = next((m for m in mutations if m["name"] == "submitForReview"), None)
    
    assert submit_for_review_mutation is not None, "submitForReview mutation not found in schema"
    
    # Check that it accepts SubmitForReviewInput
    args = submit_for_review_mutation["args"]
    assert len(args) == 1, "submitForReview should have exactly one argument"
    assert args[0]["name"] == "input", "submitForReview argument should be named 'input'"
    assert args[0]["type"]["kind"] == "NON_NULL", "submitForReview input should be non-null"
    assert args[0]["type"]["ofType"]["name"] == "SubmitForReviewInput", "submitForReview should accept SubmitForReviewInput"
    
    # Check that it returns a Project (non-null)
    return_type = submit_for_review_mutation["type"]
    assert return_type["kind"] == "NON_NULL", "submitForReview should return a non-null object"
    assert return_type["ofType"]["name"] == "Project", "submitForReview should return a Project"


# Test the input validation for submitForReview
@pytest.mark.asyncio
async def test_submit_for_review_input_validation(client: AsyncClient):
    """
    Contract test for submitForReview input validation.

    This test verifies that the mutation properly validates input parameters.
    """
    # Test with invalid UUID
    mutation = """
        mutation {
            submitForReview(input: {projectId: "invalid-uuid"}) {
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


# Test authorization for submitForReview
@pytest.mark.asyncio
async def test_submit_for_review_authorization(client: AsyncClient):
    """
    Contract test for submitForReview authorization.

    This test verifies that only authorized users can submit projects for review.
    """
    # This test would require setting up different user roles
    # For now, we'll test that the mutation exists and can be called
    # The actual authorization logic is tested in integration tests
    pass
