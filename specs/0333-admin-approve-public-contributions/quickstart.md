# Quickstart: Document Publication Workflow

## Overview
This document provides a practical guide for testing the document publication workflow with admin approval. For detailed business requirements and user workflows, see [spec.md](./spec.md).

## Prerequisites
- Running backend services (projects module)
- Valid user accounts with different roles:
  - Contributor
  - Reviewer
  - Administrator
- GraphQL client (GraphiQL, Postman, etc.)

## Testing the Workflow

This guide walks through the complete workflow to validate the implementation. Each step includes GraphQL examples and expected outcomes.

### 1. Contributor Submits Project for Review
As a Contributor, create a project and submit it for review:

```graphql
mutation {
  createProject(input: {
    name: "Sample Project"
    description: "A sample project for testing"
  }) {
    id
    name
    state
  }
}
```

Then submit the project for review:

```graphql
mutation {
  submitForReview(input: {
    projectId: "PROJECT_ID_FROM_PREVIOUS_STEP"
  }) {
    id
    name
    state
  }
}
```

**Expected Result**: Project state changes from DRAFT to IN_REVIEW

### 2. Reviewer Approves Project
As a Reviewer, find the project in the review queue and approve it:

```graphql
query {
  projectsForReview {
    id
    name
    state
    createdBy
  }
}
```

Approve the project:

```graphql
mutation {
  approveProject(input: {
    projectId: "PROJECT_ID_FROM_QUERY"
  }) {
    id
    name
    state
  }
}
```

**Expected Result**: Project state changes from IN_REVIEW to TO_PUBLISH

### 3. Administrator Publishes Project
As an Administrator, publish the approved project:

```graphql
query {
  projectsToPublish {
    id
    name
    state
  }
}
```

Publish the project:

```graphql
mutation {
  publishProject(input: {
    projectId: "PROJECT_ID_FROM_QUERY"
  }) {
    id
    name
    state
  }
}
```

**Expected Result**: Project state changes from TO_PUBLISH to DRAFT (published)

### 4. Administrator Unpublishes Project
As an Administrator, unpublish a published project:

```graphql
mutation {
  unpublishProject(input: {
    projectId: "PUBLISHED_PROJECT_ID"
  }) {
    id
    name
    state
  }
}
```

Confirm the unpublishing:

```graphql
mutation {
  unpublishProject(input: {
    projectId: "PROJECT_ID_FROM_PREVIOUS_STEP"
  }) {
    id
    name
    state
  }
}
```

**Expected Result**: Project state changes from DRAFT to TO_UNPUBLISH, then back to DRAFT

### 5. User Deletes Project
As any user, mark a project for deletion:

```graphql
mutation {
  deleteProject(input: {
    projectId: "ANY_PROJECT_ID"
  })
}
```

As an Administrator, permanently delete the project:

```graphql
mutation {
  deleteProject(input: {
    projectId: "PROJECT_ID_FROM_PREVIOUS_STEP"
  })
}
```

**Expected Result**: Project is permanently deleted

### 6. Administrator Locks/Unlocks Project
As an Administrator, lock a project to prevent modifications:

```graphql
mutation {
  lockProject(input: {
    projectId: "ANY_PROJECT_ID"
  }) {
    id
    name
    state
  }
}
```

Attempt to modify the locked project (should fail):

```graphql
mutation {
  submitForReview(input: {
    projectId: "PROJECT_ID_FROM_PREVIOUS_STEP"
  }) {
    id
    name
    state
  }
}
```

Unlock the project:

```graphql
mutation {
  unlockProject(input: {
    projectId: "PROJECT_ID_FROM_LOCK_STEP"
  }) {
    id
    name
    state
  }
}
```

**Expected Result**: Project state changes to LOCKED, modifications fail, then state returns to previous state

## Validation Points

During testing, verify these key aspects:

### Role-Based Access Control
- Contributors can only submit their own projects for review
- Reviewers can only approve/reject projects in IN_REVIEW state
- Administrators can perform all actions
- Unauthorized actions should return appropriate error messages

### State Transition Validation
- Invalid state transitions should be rejected
- Projects in LOCKED state cannot be modified
- Projects must be in correct state for each action

### Data Integrity
- Project data should be preserved during state transitions
- Created/updated timestamps should be accurate
- User assignments should be tracked correctly

## Troubleshooting

### Common Issues
1. **Permission Denied Errors**: Verify user role and project ownership
2. **Invalid State Transition**: Check current project state and user role
3. **Project Not Found**: Verify project ID is correct and accessible to user

### Debugging Steps
1. Check GraphQL response for specific error messages
2. Verify user authentication and role assignment
3. Confirm project state using direct database query if needed
4. Check service logs for detailed error information

## Next Steps
After validating the basic workflow, proceed with:
- Performance testing with large datasets
- Concurrent access testing
- Integration testing with frontend components
- Security testing with various user roles
