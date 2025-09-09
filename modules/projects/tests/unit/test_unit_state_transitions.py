import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID

from models.database.db_model import DBProject, ProjectState
from models.user_role import UserRole
from logic.project_service import ProjectService

# Mock UUIDs for testing
MOCK_PROJECT_ID = UUID("12345678-1234-5678-1234-567812345678")
MOCK_USER_ID = UUID("87654321-4321-8765-4321-876543218765")
MOCK_ASSIGNEE_ID = UUID("11111111-2222-3333-4444-555555555555")


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


@pytest.mark.asyncio
async def test_draft_to_in_review_transition():
    """Test DRAFT → IN_REVIEW transition"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    mock_project.created_by = MOCK_USER_ID
    mock_project.assigned_to = None
    mock_project.assigned_at = None
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.submit_for_review(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.CONTRIBUTOR)
        
        # Assertions
        assert result.state == ProjectState.IN_REVIEW
        assert result.assigned_to is None
        assert result.assigned_at is None
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_in_review_to_to_publish_transition():
    """Test IN_REVIEW → TO_PUBLISH transition"""
    # Create a mock project in IN_REVIEW state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.IN_REVIEW
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.approve_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.REVIEWER)
        
        # Assertions
        assert result.state == ProjectState.TO_PUBLISH
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_in_review_to_draft_transition():
    """Test IN_REVIEW → DRAFT transition"""
    # Create a mock project in IN_REVIEW state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.IN_REVIEW
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.reject_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.REVIEWER)
        
        # Assertions
        assert result.state == ProjectState.DRAFT
        assert result.assigned_to is None
        assert result.assigned_at is None
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_to_publish_to_draft_transition():
    """Test TO_PUBLISH → DRAFT transition"""
    # Create a mock project in TO_PUBLISH state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.TO_PUBLISH
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.publish_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.DRAFT
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_draft_to_to_unpublish_transition():
    """Test DRAFT → TO_UNPUBLISH transition"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.unpublish_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.TO_UNPUBLISH
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_any_state_to_locked_transition():
    """Test any state → LOCKED transition"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.lock_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.LOCKED
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_locked_to_previous_state_transition():
    """Test LOCKED → previous state transition"""
    # Create a mock project in LOCKED state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.LOCKED
    mock_project.previous_state = ProjectState.DRAFT.value
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Call the method
        result = await ProjectService.unlock_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.ADMINISTRATOR)
        
        # Assertions
        assert result.state == ProjectState.DRAFT
        mock_project.save.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_transitions():
    """Test invalid state transitions"""
    # Create a mock project in DRAFT state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.DRAFT
    mock_project.created_by = MOCK_USER_ID
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Test that a CONTRIBUTOR cannot approve a project (which requires REVIEWER role)
        with pytest.raises(ValueError, match="User does not have permission to approve this project"):
            await ProjectService.approve_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.CONTRIBUTOR)


@pytest.mark.asyncio
async def test_state_transition_validation():
    """Test state transition validation logic"""
    # Create a mock project in IN_REVIEW state
    mock_project = MagicMock(spec=DBProject)
    mock_project.id = MOCK_PROJECT_ID
    mock_project.state = ProjectState.IN_REVIEW
    
    # Mock the DBProject.get method to return our mock project
    with patch('logic.project_service.DBProject.get', new=AsyncMock(return_value=mock_project)):
        # Mock the save method
        mock_project.save = AsyncMock()
        
        # Test that a REVIEWER can approve a project in IN_REVIEW state
        result = await ProjectService.approve_project(MOCK_PROJECT_ID, MOCK_USER_ID, UserRole.REVIEWER)
        
        # Assertions
        assert result.state == ProjectState.TO_PUBLISH
        mock_project.save.assert_called_once()
