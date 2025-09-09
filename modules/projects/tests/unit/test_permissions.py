import pytest
from unittest.mock import MagicMock
from uuid import UUID

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.permissions import (
    has_permission,
    validate_project_ownership,
    validate_project_assignment,
    can_submit_for_review,
    can_approve_project,
    can_reject_project,
    can_publish_project,
    can_unpublish_project,
    can_delete_project,
    can_lock_project,
    can_unlock_project,
    can_assign_project,
)

# Mock UUIDs for testing
MOCK_PROJECT_ID = UUID("12345678-1234-5678-1234-567812345678")
MOCK_USER_ID = UUID("87654321-4321-8765-4321-876543218765")
MOCK_OTHER_USER_ID = UUID("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def mock_db_project():
    """Create a mock DBProject for testing"""
    project = MagicMock(spec=DBProject)
    project.id = MOCK_PROJECT_ID
    project.state = ProjectState.DRAFT
    project.created_by = MOCK_USER_ID
    project.assigned_to = None
    project.assigned_at = None
    return project


def test_has_permission():
    """Test has_permission function"""
    # Test role hierarchy: CONTRIBUTOR < REVIEWER < ADMINISTRATOR
    assert has_permission(UserRole.CONTRIBUTOR, UserRole.CONTRIBUTOR) == True
    assert has_permission(UserRole.REVIEWER, UserRole.CONTRIBUTOR) == True
    assert has_permission(UserRole.ADMINISTRATOR, UserRole.CONTRIBUTOR) == True
    assert has_permission(UserRole.CONTRIBUTOR, UserRole.REVIEWER) == False
    assert has_permission(UserRole.REVIEWER, UserRole.REVIEWER) == True
    assert has_permission(UserRole.ADMINISTRATOR, UserRole.REVIEWER) == True
    assert has_permission(UserRole.CONTRIBUTOR, UserRole.ADMINISTRATOR) == False
    assert has_permission(UserRole.REVIEWER, UserRole.ADMINISTRATOR) == False
    assert has_permission(UserRole.ADMINISTRATOR, UserRole.ADMINISTRATOR) == True


def test_validate_project_ownership():
    """Test validate_project_ownership function"""
    # Create a mock project owned by MOCK_USER_ID
    project = MagicMock(spec=DBProject)
    project.created_by = MOCK_USER_ID
    
    # Test ownership validation
    assert validate_project_ownership(project, MOCK_USER_ID) == True
    assert validate_project_ownership(project, MOCK_OTHER_USER_ID) == False


def test_validate_project_assignment():
    """Test validate_project_assignment function"""
    # Create a mock project assigned to MOCK_USER_ID
    project = MagicMock(spec=DBProject)
    project.assigned_to = MOCK_USER_ID
    
    # Test assignment validation
    assert validate_project_assignment(project, MOCK_USER_ID) == True
    assert validate_project_assignment(project, MOCK_OTHER_USER_ID) == False
    
    # Test unassigned project
    project.assigned_to = None
    assert validate_project_assignment(project, MOCK_USER_ID) == False


def test_can_submit_for_review():
    """Test can_submit_for_review function"""
    # Create a mock project in DRAFT state owned by MOCK_USER_ID
    project = MagicMock(spec=DBProject)
    project.state = ProjectState.DRAFT
    project.created_by = MOCK_USER_ID
    
    # Test valid case: CONTRIBUTOR user owning the project in DRAFT state
    assert can_submit_for_review(project, UserRole.CONTRIBUTOR, MOCK_USER_ID) == True
    
    # Test valid case: ADMINISTRATOR user with project in DRAFT state
    assert can_submit_for_review(project, UserRole.ADMINISTRATOR, MOCK_USER_ID) == True
    assert can_submit_for_review(project, UserRole.ADMINISTRATOR, MOCK_OTHER_USER_ID) == True
    
    # Test invalid cases
    assert can_submit_for_review(project, UserRole.REVIEWER, MOCK_USER_ID) == False
    assert can_submit_for_review(project, UserRole.CONTRIBUTOR, MOCK_OTHER_USER_ID) == False
    
    # Test wrong state
    project.state = ProjectState.IN_REVIEW
    assert can_submit_for_review(project, UserRole.CONTRIBUTOR, MOCK_USER_ID) == False
    assert can_submit_for_review(project, UserRole.ADMINISTRATOR, MOCK_USER_ID) == False


def test_can_approve_project():
    """Test can_approve_project function"""
    # Create a mock project in IN_REVIEW state
    project = MagicMock(spec=DBProject)
    project.state = ProjectState.IN_REVIEW
    
    # Test valid case: REVIEWER user with project in IN_REVIEW state
    assert can_approve_project(project, UserRole.REVIEWER) == True
    
    # Test invalid cases
    assert can_approve_project(project, UserRole.CONTRIBUTOR) == False
    # Test that ADMINISTRATOR can also approve projects
    assert can_approve_project(project, UserRole.ADMINISTRATOR) == True
    
    # Test wrong state
    project.state = ProjectState.DRAFT
    assert can_approve_project(project, UserRole.REVIEWER) == False


def test_can_reject_project():
    """Test can_reject_project function"""
    # Create a mock project in IN_REVIEW state
    project = MagicMock(spec=DBProject)
    project.state = ProjectState.IN_REVIEW
    
    # Test valid case: REVIEWER user with project in IN_REVIEW state
    assert can_reject_project(project, UserRole.REVIEWER) == True
    
    # Test invalid cases
    assert can_reject_project(project, UserRole.CONTRIBUTOR) == False
    # Test that ADMINISTRATOR can also reject projects
    assert can_reject_project(project, UserRole.ADMINISTRATOR) == True
    
    # Test wrong state
    project.state = ProjectState.DRAFT
    assert can_reject_project(project, UserRole.REVIEWER) == False


def test_can_publish_project():
    """Test can_publish_project function"""
    # Create a mock project in TO_PUBLISH state
    project = MagicMock(spec=DBProject)
    project.state = ProjectState.TO_PUBLISH
    
    # Test valid case: ADMINISTRATOR user with project in TO_PUBLISH state
    assert can_publish_project(project, UserRole.ADMINISTRATOR) == True
    
    # Test invalid cases
    assert can_publish_project(project, UserRole.CONTRIBUTOR) == False
    assert can_publish_project(project, UserRole.REVIEWER) == False
    
    # Test wrong state
    project.state = ProjectState.DRAFT
    assert can_publish_project(project, UserRole.ADMINISTRATOR) == False


def test_can_unpublish_project():
    """Test can_unpublish_project function"""
    # Create a mock project in DRAFT state
    project = MagicMock(spec=DBProject)
    project.state = ProjectState.DRAFT
    
    # Test valid case: ADMINISTRATOR user with project in DRAFT state
    assert can_unpublish_project(project, UserRole.ADMINISTRATOR) == True
    
    # Test invalid cases
    assert can_unpublish_project(project, UserRole.CONTRIBUTOR) == False
    assert can_unpublish_project(project, UserRole.REVIEWER) == False
    
    # Test wrong state
    project.state = ProjectState.IN_REVIEW
    assert can_unpublish_project(project, UserRole.ADMINISTRATOR) == False


def test_can_delete_project():
    """Test can_delete_project function"""
    # Create a mock project not in LOCKED state
    project = MagicMock(spec=DBProject)
    project.state = ProjectState.DRAFT
    project.created_by = MOCK_USER_ID
    
    # Test valid cases
    assert can_delete_project(project, UserRole.CONTRIBUTOR, MOCK_USER_ID) == True
    assert can_delete_project(project, UserRole.ADMINISTRATOR, MOCK_OTHER_USER_ID) == True
    
    # Test invalid cases
    assert can_delete_project(project, UserRole.CONTRIBUTOR, MOCK_OTHER_USER_ID) == False
    
    # Test locked project
    project.state = ProjectState.LOCKED
    assert can_delete_project(project, UserRole.CONTRIBUTOR, MOCK_USER_ID) == False
    assert can_delete_project(project, UserRole.ADMINISTRATOR, MOCK_OTHER_USER_ID) == False


def test_can_lock_project():
    """Test can_lock_project function"""
    # Test valid case: ADMINISTRATOR user
    assert can_lock_project(UserRole.ADMINISTRATOR) == True
    
    # Test invalid cases
    assert can_lock_project(UserRole.CONTRIBUTOR) == False
    assert can_lock_project(UserRole.REVIEWER) == False


def test_can_unlock_project():
    """Test can_unlock_project function"""
    # Create a mock project in LOCKED state
    project = MagicMock(spec=DBProject)
    project.state = ProjectState.LOCKED
    
    # Test valid case: ADMINISTRATOR user with project in LOCKED state
    assert can_unlock_project(project, UserRole.ADMINISTRATOR) == True
    
    # Test invalid cases
    assert can_unlock_project(project, UserRole.CONTRIBUTOR) == False
    assert can_unlock_project(project, UserRole.REVIEWER) == False
    
    # Test wrong state
    project.state = ProjectState.DRAFT
    assert can_unlock_project(project, UserRole.ADMINISTRATOR) == False


def test_can_assign_project():
    """Test can_assign_project function"""
    # Test valid case: ADMINISTRATOR user
    assert can_assign_project(UserRole.ADMINISTRATOR) == True
    
    # Test invalid cases
    assert can_assign_project(UserRole.CONTRIBUTOR) == False
    assert can_assign_project(UserRole.REVIEWER) == False
