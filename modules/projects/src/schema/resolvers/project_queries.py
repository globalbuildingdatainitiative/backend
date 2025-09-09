import logging
from typing import List
from uuid import UUID

import strawberry
from strawberry.types import Info

from core.context import get_user
from models.database.db_model import DBProject
from models.openbdf.types import GraphQLProject, GraphQLProjectState
from logic.project_service import ProjectService
from schema.project_schema import ProjectsByStateInput

logger = logging.getLogger(__name__)


async def projects_by_state_resolver(info: Info, input: ProjectsByStateInput) -> List[GraphQLProject]:
    """
    Get projects by state
    """
    user = get_user(info)
    projects = await ProjectService.get_projects_by_state(input.state, user.id, user.role)
    return [GraphQLProject.from_pydantic(project) for project in projects]


async def projects_for_review_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are in review (IN_REVIEW state)
    """
    user = get_user(info)
    projects = await ProjectService.get_projects_for_review(user.id)
    return [GraphQLProject.from_pydantic(project) for project in projects]


async def projects_to_publish_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are ready to publish (TO_PUBLISH state)
    """
    user = get_user(info)
    projects = await ProjectService.get_projects_to_publish(user.id)
    return [GraphQLProject.from_pydantic(project) for project in projects]


async def projects_to_unpublish_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are marked for unpublishing (TO_UNPUBLISH state)
    """
    user = get_user(info)
    projects = await ProjectService.get_projects_to_unpublish(user.id)
    return [GraphQLProject.from_pydantic(project) for project in projects]


async def projects_to_delete_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects that are marked for deletion (TO_DELETE state)
    """
    user = get_user(info)
    projects = await ProjectService.get_projects_to_delete(user.id)
    return [GraphQLProject.from_pydantic(project) for project in projects]


async def my_projects_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects created by the current user
    """
    user = get_user(info)
    projects = await ProjectService.get_my_projects(user.id)
    return [GraphQLProject.from_pydantic(project) for project in projects]


async def assigned_projects_resolver(info: Info) -> List[GraphQLProject]:
    """
    Get projects assigned to the current reviewer
    """
    user = get_user(info)
    projects = await ProjectService.get_assigned_projects(user.id)
    return [GraphQLProject.from_pydantic(project) for project in projects]
