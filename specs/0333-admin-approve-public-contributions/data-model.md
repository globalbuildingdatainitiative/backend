# Data Model: Document Publication Workflow

## Overview
This document describes the data model for the document publication workflow with admin approval. The model extends the existing project contribution system to add state management and role-based permissions. For business requirements and user workflows, see [spec.md](./spec.md).

**Status**: Implemented
**Last Updated**: 2025-09-09

## Overview
This document describes the data model for the document publication workflow with admin approval. The model extends the existing project contribution system to add state management and role-based permissions. For business requirements and user workflows, see [spec.md](./spec.md).

## Entities

### ProjectState (Enum)
Enumeration of possible project states in the publication workflow. See [spec.md](./spec.md) for business context.

Values:
- DRAFT: The project is being added or edited and is not yet ready for review
- IN_REVIEW: The project is ready for review by a reviewer
- TO_PUBLISH: The project has been reviewed and approved for publication by a reviewer
- TO_UNPUBLISH: The project is currently published and needs to be unpublished by an administrator
- TO_DELETE: The project is marked for deletion by an administrator
- LOCKED: The project is locked by an administrator and cannot be edited, (un)published or deleted

### UserRoles (Enum)
Enumeration of user roles in the system. See [spec.md](./spec.md) for business context.

Values:
- CONTRIBUTOR: Can add and edit their own project contributions
- REVIEWER: Can add and edit all project contributions but cannot (un)publish, or delete them
- ADMINISTRATOR: Can perform all operations, including project (un)publication and deletion

### Project (Extended Model)
Extends the existing DBProject model with state management.

Fields:
- id: UUID (inherited)
- name: String (inherited)
- description: String (inherited)
- ... (other inherited fields from LCAxProject)
- state: ProjectState (new field)
- created_by: UUID (new field - references user who created the project)
- assigned_to: UUID (optional, new field - references user assigned to review/project)
- assigned_at: DateTime (optional, new field - when assignment occurred)

Relationships:
- contribution: BackLink to DBContribution (inherited)
- assemblies: List of Link to DBAssembly (inherited)

Validation Rules:
- State transitions must follow the defined workflow
- Only users with appropriate roles can perform state transitions
- LOCKED projects cannot be modified
- Only ADMINISTRATOR users can lock/unlock projects


### Contribution (Extended Model)
Extends the existing DBContribution model to support the workflow.

Fields:
- id: UUID (inherited)
- uploaded_at: DateTime (inherited)
- user_id: UUID (inherited)
- organization_id: UUID (inherited)
- public: Boolean (inherited)
- project: Link to DBProject (inherited, but now with state management)

## Database Schema
The models will be stored in MongoDB using the Beanie ODM. The extended models will maintain compatibility with existing data structures while adding the new state management fields.

Indexes:
- project.state: Indexed for efficient querying by state
- project.created_by: Indexed for user-specific queries
- project.assigned_to: Indexed for reviewer queues

## Service Layer
The service layer will handle:
- State transition validation
- Permission checking based on user roles
- Notification sending on state changes
- Assignment management

## API Contracts
GraphQL mutations will be provided for each state transition. For business context of these operations, see [spec.md](./spec.md):

- submitForReview(projectId: UUID): Project
- approveProject(projectId: UUID): Project
- rejectProject(projectId: UUID): Project
- publishProject(projectId: UUID): Project
- unpublishProject(projectId: UUID): Project
- deleteProject(projectId: UUID): Boolean
- lockProject(projectId: UUID): Project
- unlockProject(projectId: UUID): Project
- assignProject(projectId: UUID, userId: UUID): Project

Queries:
- projectsByState(state: ProjectState): [Project]
- projectsForReview: [Project] (IN_REVIEW state)
- projectsToPublish: [Project] (TO_PUBLISH state)
- projectsToUnpublish: [Project] (TO_UNPUBLISH state)
- projectsToDelete: [Project] (TO_DELETE state)
- myProjects: [Project] (projects created by current user)
- assignedProjects: [Project] (projects assigned to current reviewer)
