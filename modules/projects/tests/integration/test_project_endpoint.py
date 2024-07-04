import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_projects_query(client: AsyncClient, projects):
    query = """
        query {
            projects {
                items {
                    id
                    name
                    assemblies {
                        id
                        name
                    }
                }
                count
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("items")
    assert data.get("data", {}).get("projects", {}).get("count") == len(projects)
    assert data.get("data", {}).get("projects", {}).get("items", [])[0].get("assemblies")


@pytest.mark.asyncio
async def test_projects_query_filter(client: AsyncClient, projects):
    query = """
        query($id: UUID!) {
            projects {
                items(filterBy: {id: {equal: $id}}) {
                    id
                    name
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {"id": str(projects[0].id)}
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert len(data.get("data", {}).get("projects", {}).get("items")) == 1
    assert data.get("data", {}).get("projects", {}).get("items", [])[0].get("id") == str(projects[0].id)


@pytest.mark.asyncio
async def test_projects_query_sort(client: AsyncClient, projects):
    query = """
        query {
            projects {
                items(sortBy: {id: ASC}) {
                    id
                    name
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("items")
    assert data.get("data", {}).get("projects", {}).get("items", []) == [
        project.model_dump(include={"id", "name"}, mode='json') for project in sorted(projects, key=lambda p: p.id)]


@pytest.mark.asyncio
async def test_projects_query_offset(client: AsyncClient, projects):
    query = """
        query {
            projects {
                items(offset: 2) {
                    id
                    name
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("items")
    assert data.get("data", {}).get("projects", {}).get("items", [])[0].get("id") == str(projects[2].id)


@pytest.mark.asyncio
@pytest.mark.parametrize("group_by", ["name", "location.country"])
async def test_projects_query_groups(client: AsyncClient, projects, group_by):
    query = """
        query($groupBy: String!) {
            projects {
                groups(groupBy: $groupBy) {
                    group
                    items {
                        id
                        name
                    }
                    count
                }  
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
            "variables": {
                "groupBy": group_by
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("groups")
    assert data.get("data", {}).get("projects", {}).get("groups")[0].get("items", [])[0].get("id") == str(
        projects[0].id)


@pytest.mark.asyncio
async def test_projects_query_aggregate(client: AsyncClient, projects):
    query = """
        query {
            projects {
                aggregation(apply: [{method: AVG, field: "reference_study_period"}]) {
                    method
                    field
                    value
                }
            }
        }
    """

    response = await client.post(
        f"{settings.API_STR}/graphql",
        json={
            "query": query,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert not data.get("errors")
    assert data.get("data", {}).get("projects", {}).get("aggregation")
    assert data.get("data", {}).get("projects", {}).get("aggregation", [])[0] == {"method": "AVG",
                                                                                  "field": "reference_study_period",
                                                                                  "value": 50}
