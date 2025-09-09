# Tasks: Document Publication Workflow with Admin Approval

**Input**: Design documents from `/specs/0333-admin-approve-public-contributions/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

For business requirements and user workflows, see [spec.md](./spec.md).
For technical data model details, see [data-model.md](./data-model.md).
For implementation decisions and rationale, see [research.md](./research.md).
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `backend/src/`, `frontend/src/`
- All paths are relative to the backend module directory

## Phase 3.1: Setup
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with FastAPI/Strawberry dependencies
- [ ] T003 [P] Configure linting and formatting tools for projects module

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] T004 [P] Contract test for submitForReview mutation in backend/modules/projects/tests/contract/test_submit_for_review.py
- [ ] T005 [P] Contract test for approveProject mutation in backend/modules/projects/tests/contract/test_approve_project.py
- [ ] T006 [P] Contract test for rejectProject mutation in backend/modules/projects/tests/contract/test_reject_project.py
- [ ] T007 [P] Contract test for publishProject mutation in backend/modules/projects/tests/contract/test_publish_project.py
- [ ] T008 [P] Contract test for unpublishProject mutation in backend/modules/projects/tests/contract/test_unpublish_project.py
- [ ] T009 [P] Contract test for deleteProject mutation in backend/modules/projects/tests/contract/test_delete_project.py
- [ ] T010 [P] Contract test for lockProject mutation in backend/modules/projects/tests/contract/test_lock_project.py
- [ ] T011 [P] Contract test for unlockProject mutation in backend/modules/projects/tests/contract/test_unlock_project.py
- [ ] T012 [P] Contract test for assignProject mutation in backend/modules/projects/tests/contract/test_assign_project.py
- [ ] T013 [P] Contract test for projectsByState query in backend/modules/projects/tests/contract/test_projects_by_state.py
- [ ] T014 [P] Contract test for projectsForReview query in backend/modules/projects/tests/contract/test_projects_for_review.py
- [ ] T015 [P] Contract test for projectsToPublish query in backend/modules/projects/tests/contract/test_projects_to_publish.py
- [ ] T016 [P] Contract test for projectsToUnpublish query in backend/modules/projects/tests/contract/test_projects_to_unpublish.py
- [ ] T017 [P] Contract test for projectsToDelete query in backend/modules/projects/tests/contract/test_projects_to_delete.py
- [ ] T018 [P] Contract test for myProjects query in backend/modules/projects/tests/contract/test_my_projects.py
- [ ] T019 [P] Contract test for assignedProjects query in backend/modules/projects/tests/contract/test_assigned_projects.py

### Integration Tests
- [ ] T020 [P] Integration test for contributor submitting project for review in backend/modules/projects/tests/integration/test_contributor_submit_for_review.py
- [ ] T021 [P] Integration test for reviewer approving project in backend/modules/projects/tests/integration/test_reviewer_approve_project.py
- [ ] T022 [P] Integration test for reviewer rejecting project in backend/modules/projects/tests/integration/test_reviewer_reject_project.py
- [ ] T023 [P] Integration test for administrator publishing project in backend/modules/projects/tests/integration/test_admin_publish_project.py
- [ ] T024 [P] Integration test for administrator unpublishing project in backend/modules/projects/tests/integration/test_admin_unpublish_project.py
- [ ] T025 [P] Integration test for user deleting project in backend/modules/projects/tests/integration/test_user_delete_project.py
- [ ] T026 [P] Integration test for administrator locking/unlocking project in backend/modules/projects/tests/integration/test_admin_lock_unlock_project.py
- [ ] T027 [P] Integration test for administrator assigning project in backend/modules/projects/tests/integration/test_admin_assign_project.py
- [ ] T028 [P] Integration test for role-based access control in backend/modules/projects/tests/integration/test_role_based_access.py
- [ ] T029 [P] Integration test for state transition validation in backend/modules/projects/tests/integration/test_state_transitions.py
- [ ] T030 [P] Integration test for concurrent access in backend/modules/projects/tests/integration/test_concurrent_access.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
### Model Extensions
- [ ] T031 [P] Extend DBProject model with state management in backend/modules/projects/src/models/database/db_model.py
- [ ] T032 [P] Extend GraphQLProject with state fields in backend/modules/projects/src/models/openbdf/project.py
- [ ] T033 [P] Create ProjectState enum in backend/modules/projects/src/models/project_state.py
- [ ] T034 [P] Create UserRole enum in backend/modules/projects/src/models/user_role.py

### Service Layer
- [ ] T035 ProjectService for state transitions in backend/modules/projects/src/logic/project_service.py
- [ ] T036 [P] Permission validation functions in backend/modules/projects/src/logic/permissions.py
- [ ] T037 [P] Notification service integration in backend/modules/projects/src/logic/notifications.py
- [ ] T038 [P] Assignment management in backend/modules/projects/src/logic/assignment.py

### GraphQL Schema
- [ ] T039 Extend GraphQL schema with new types and enums in backend/modules/projects/src/schema/project_schema.py
- [ ] T040 [P] Implement submitForReview resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T041 [P] Implement approveProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T042 [P] Implement rejectProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T043 [P] Implement publishProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T044 [P] Implement unpublishProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T045 [P] Implement deleteProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T046 [P] Implement lockProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T047 [P] Implement unlockProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T048 [P] Implement assignProject resolver in backend/modules/projects/src/schema/resolvers/project_mutations.py
- [ ] T049 [P] Implement projectsByState resolver in backend/modules/projects/src/schema/resolvers/project_queries.py
- [ ] T050 [P] Implement projectsForReview resolver in backend/modules/projects/src/schema/resolvers/project_queries.py
- [ ] T051 [P] Implement projectsToPublish resolver in backend/modules/projects/src/schema/resolvers/project_queries.py
- [ ] T052 [P] Implement projectsToUnpublish resolver in backend/modules/projects/src/schema/resolvers/project_queries.py
- [ ] T053 [P] Implement projectsToDelete resolver in backend/modules/projects/src/schema/resolvers/project_queries.py
- [ ] T054 [P] Implement myProjects resolver in backend/modules/projects/src/schema/resolvers/project_queries.py
- [ ] T055 [P] Implement assignedProjects resolver in backend/modules/projects/src/schema/resolvers/project_queries.py

## Phase 3.4: Integration
- [ ] T056 Connect ProjectService to MongoDB with proper indexing
- [ ] T057 Implement audit logging for state transitions
- [ ] T058 Add database migrations for new fields
- [ ] T059 Implement error handling and custom GraphQL errors
- [ ] T060 Add input validation for all mutations
- [ ] T061 Implement pagination for list queries
- [ ] T062 Add proper transaction support for state transitions

## Phase 3.5: Polish
- [ ] T063 [P] Unit tests for ProjectService in backend/modules/projects/tests/unit/test_project_service.py
- [ ] T064 [P] Unit tests for permission validation in backend/modules/projects/tests/unit/test_permissions.py
- [ ] T065 [P] Unit tests for state transition logic in backend/modules/projects/tests/unit/test_state_transitions.py
- [ ] T066 Performance tests for state transitions (<200ms)
- [ ] T067 [P] Update backend/modules/projects/README.md with new API documentation
- [ ] T068 [P] Update GraphQL schema documentation
- [ ] T069 Run manual-testing.md following quickstart guide
- [ ] T070 Remove any code duplication and optimize

## Dependencies
- Tests (T004-T030) before implementation (T031-T055)
- T031 blocks T035, T039
- T035 blocks T040-T055
- T056-T062 before polish (T063-T070)
- Implementation before polish (T063-T070)

## Parallel Example
```
# Launch contract tests together:
Task: "Contract test for submitForReview mutation in backend/modules/projects/tests/contract/test_submit_for_review.py"
Task: "Contract test for approveProject mutation in backend/modules/projects/tests/contract/test_approve_project.py"
Task: "Contract test for rejectProject mutation in backend/modules/projects/tests/contract/test_reject_project.py"
Task: "Contract test for publishProject mutation in backend/modules/projects/tests/contract/test_publish_project.py"

# Launch integration tests together:
Task: "Integration test for contributor submitting project for review in backend/modules/projects/tests/integration/test_contributor_submit_for_review.py"
Task: "Integration test for reviewer approving project in backend/modules/projects/tests/integration/test_reviewer_approve_project.py"
Task: "Integration test for reviewer rejecting project in backend/modules/projects/tests/integration/test_reviewer_reject_project.py"
Task: "Integration test for administrator publishing project in backend/modules/projects/tests/integration/test_admin_publish_project.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
