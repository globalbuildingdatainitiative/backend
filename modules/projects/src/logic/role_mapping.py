import logging
from typing import List

# Handle AuthRole import for tests
try:
    from backend.modules.auth.src.models.roles import Role as AuthRole
except ImportError:
    # Create a mock AuthRole for testing purposes
    from enum import Enum
    class AuthRole(str, Enum):
        OWNER = "OWNER"
        MEMBER = "MEMBER"
        ADMIN = "ADMIN"

from models.user_role import UserRole

logger = logging.getLogger(__name__)


def map_auth_roles_to_project_roles(auth_roles: List[AuthRole]) -> List[UserRole]:
    """
    Map auth module roles to project module roles.
    
    Mapping:
    - AUTH OWNER → PROJECT CONTRIBUTOR
    - AUTH MEMBER → PROJECT CONTRIBUTOR
    - AUTH ADMIN → PROJECT ADMINISTRATOR
    
    For REVIEWER role, we'll need to implement organization-level permissions
    or add a specific reviewer role in the auth module.
    
    Args:
        auth_roles: List of roles from the auth module
        
    Returns:
        List of mapped project roles
    """
    project_roles = []
    
    # Map each auth role to project roles
    for role in auth_roles:
        if role == AuthRole.ADMIN:
            # Admins get all project roles
            project_roles.extend([UserRole.CONTRIBUTOR, UserRole.REVIEWER, UserRole.ADMINISTRATOR])
        elif role in [AuthRole.OWNER, AuthRole.MEMBER]:
            # Owners and members are contributors
            if UserRole.CONTRIBUTOR not in project_roles:
                project_roles.append(UserRole.CONTRIBUTOR)
    
    # Remove duplicates while preserving order
    unique_roles = []
    for role in project_roles:
        if role not in unique_roles:
            unique_roles.append(role)
    
    return unique_roles


def get_highest_project_role(auth_roles: List[AuthRole]) -> UserRole:
    """
    Get the highest privilege project role from auth roles.
    
    Args:
        auth_roles: List of roles from the auth module
        
    Returns:
        Highest privilege project role
    """
    project_roles = map_auth_roles_to_project_roles(auth_roles)
    
    # Define role hierarchy (higher index = higher privilege)
    role_hierarchy = [UserRole.CONTRIBUTOR, UserRole.REVIEWER, UserRole.ADMINISTRATOR]
    
    # Find the highest role
    highest_role = UserRole.CONTRIBUTOR  # Default to lowest role
    for role in project_roles:
        if role_hierarchy.index(role) > role_hierarchy.index(highest_role):
            highest_role = role
    
    return highest_role


def has_project_role(auth_roles: List[AuthRole], required_role: UserRole) -> bool:
    """
    Check if user has the required project role based on their auth roles.
    
    Args:
        auth_roles: List of roles from the auth module
        required_role: Required project role
        
    Returns:
        True if user has required role, False otherwise
    """
    project_roles = map_auth_roles_to_project_roles(auth_roles)
    return required_role in project_roles
