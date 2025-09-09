from enum import Enum


class ProjectState(str, Enum):
    """
    Enumeration of possible project states in the publication workflow.

    Values:
    - DRAFT: The project is being added or edited and is not yet ready for review
    - IN_REVIEW: The project is ready for review by a reviewer
    - TO_PUBLISH: The project has been reviewed and approved for publication by a reviewer
    - TO_UNPUBLISH: The project is currently published and needs to be unpublished by an administrator
    - TO_DELETE: The project is marked for deletion by an administrator
    - LOCKED: The project is locked by an administrator and cannot be edited, (un)published or deleted
    """

    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    TO_PUBLISH = "TO_PUBLISH"
    TO_UNPUBLISH = "TO_UNPUBLISH"
    TO_DELETE = "TO_DELETE"
    LOCKED = "LOCKED"
