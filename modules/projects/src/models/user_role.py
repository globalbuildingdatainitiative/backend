from enum import Enum


class UserRole(str, Enum):
    """
    Enumeration of user roles in the system.

    Values:
    - CONTRIBUTOR: Can add and edit their own project contributions
    - REVIEWER: Can add and edit all project contributions but cannot (un)publish, or delete them
    - ADMINISTRATOR: Can perform all operations, including project (un)publication and deletion
    """

    CONTRIBUTOR = "CONTRIBUTOR"
    REVIEWER = "REVIEWER"
    ADMINISTRATOR = "ADMINISTRATOR"
