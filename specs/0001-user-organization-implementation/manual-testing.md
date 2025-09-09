# Manual Testing Plan: User-Organization Relationship Management

## Overview
This document provides step-by-step instructions for manually testing the User-Organization Relationship Management feature to ensure it meets the specification requirements and handles edge cases appropriately.

## Prerequisites
1. Development environment with all services running
2. Access to GraphQL playground or similar tool
3. Test user accounts with different roles
4. Access to service logs for verification

## Test Environment Setup
1. Start all services (auth, organization, router)
2. Ensure MongoDB is running and accessible
3. Ensure SuperTokens is running and accessible
4. Verify GraphQL endpoint is accessible

## Test Cases

### TC-001: Successful Organization Creation
**Objective:** Verify that a user can successfully create an organization

**Preconditions:**
- Authenticated user with OWNER role
- Valid organization data

**Steps:**
1. Navigate to GraphQL playground
2. Execute the following mutation:
```graphql
mutation {
  createOrganizations(organizations: [{
    name: "Test Organization"
    address: "123 Test Street"
    city: "Test City"
    country: CHE
    metaData: {
      stakeholders: [BUILDING_DATA_OWNERS]
    }
  }]) {
    id
    name
    address
    city
    country
    metaData {
      stakeholders
    }
  }
}
```
3. Observe response
4. Check service logs for verification messages

**Expected Results:**
- Response contains created organization with valid ID
- Organization is stored in MongoDB
- User metadata is updated with organization ID
- OWNER role is assigned to user
- Verification log message appears
- No errors in response

**Post-conditions:**
- Organization exists in database
- User has organization ID in metadata

### TC-002: User Profile Retrieval with Organization
**Objective:** Verify that a user's profile can be retrieved with organization details

**Preconditions:**
- User with associated organization (from TC-001)

**Steps:**
1. Navigate to GraphQL playground
2. Execute the following query:
```graphql
query getCurrentUser($id: String!) {
  users {
    items(filterBy: { equal: { id: $id } }, limit: 1) {
      id
      firstName
      lastName
      email
      roles
      organization {
        id
        name
        address
        city
        country
        metaData {
          stakeholders
        }
      }
      timeJoined
    }
  }
}
```
3. Provide user ID as variable
4. Observe response

**Expected Results:**
- Response contains user profile data
- Organization details are included and match created organization
- No errors in response

**Post-conditions:**
- User profile retrieved successfully

### TC-003: User Profile Retrieval without Organization
**Objective:** Verify that a user's profile can be retrieved when no organization is associated

**Preconditions:**
- User without associated organization

**Steps:**
1. Navigate to GraphQL playground
2. Execute the getCurrentUser query (same as TC-002)
3. Provide user ID without organization as variable
4. Observe response

**Expected Results:**
- Response contains user profile data
- Organization field is null
- No errors in response

**Post-conditions:**
- User profile retrieved successfully

### TC-004: Organization Resolution with Missing Organization
**Objective:** Verify graceful handling when user metadata references non-existent organization

**Preconditions:**
- User with organization ID that doesn't exist in database

**Setup:**
1. Manually update user metadata in SuperTokens to reference non-existent organization ID
2. Ensure organization with that ID doesn't exist in MongoDB

**Steps:**
1. Navigate to GraphQL playground
2. Execute the getCurrentUser query
3. Provide user ID as variable
4. Observe response
5. Check service logs for warning messages

**Expected Results:**
- Response contains user profile data
- Organization field is null
- Warning message in logs about missing organization
- No errors in response

**Post-conditions:**
- User profile retrieved successfully
- Logs contain appropriate warning

### TC-005: Concurrent Organization Access
**Objective:** Verify that concurrent requests for user-organization data are handled correctly

**Preconditions:**
- Multiple users with associated organizations

**Steps:**
1. Prepare multiple browser tabs/windows with GraphQL playground
2. Execute getCurrentUser queries simultaneously for different users
3. Observe responses and timing
4. Check service logs for any race conditions

**Expected Results:**
- All requests complete successfully
- Correct organization data returned for each user
- No race conditions or data corruption
- Consistent response times

**Post-conditions:**
- All user profiles retrieved successfully

### TC-006: Organization Creation Timing Issue Simulation
**Objective:** Verify that the verification step prevents timing issues

**Preconditions:**
- Authenticated user with OWNER role

**Steps:**
1. Navigate to GraphQL playground
2. Execute createOrganizations mutation
3. Immediately execute getCurrentUser query for the same user
4. Observe both responses
5. Check service logs for verification messages

**Expected Results:**
- Organization creation succeeds
- Immediate user query returns organization details
- Verification log message appears
- No "list index out of range" errors

**Post-conditions:**
- Organization created and accessible

### TC-007: Error Handling in Federation
**Objective:** Verify proper error handling when auth service is unavailable

**Preconditions:**
- Authenticated user
- Organization service running
- Auth service temporarily unavailable (simulate by stopping service)

**Steps:**
1. Stop auth service
2. Navigate to GraphQL playground
3. Execute getCurrentUser query
4. Observe response
5. Check organization service logs

**Expected Results:**
- Appropriate error response from GraphQL
- Error logged in organization service
- No service crashes

**Post-conditions:**
- Services restored to normal operation

## Edge Case Testing

### EC-001: Invalid Organization Data
**Objective:** Verify validation of organization creation data

**Steps:**
1. Execute createOrganizations mutation with invalid data (e.g., missing required fields)
2. Observe response

**Expected Results:**
- Appropriate validation error response
- No organization created
- No user metadata modified

### EC-002: Very Large Organization Metadata
**Objective:** Verify handling of large organization metadata

**Steps:**
1. Execute createOrganizations mutation with very large stakeholders list
2. Observe response and performance

**Expected Results:**
- Organization created successfully
- Reasonable response time
- No memory issues

### EC-003: Unicode Characters in Organization Data
**Objective:** Verify handling of unicode characters

**Steps:**
1. Execute createOrganizations mutation with unicode characters in name/address
2. Retrieve user profile with organization
3. Observe response

**Expected Results:**
- Organization created successfully
- Unicode characters preserved
- No encoding issues

## Performance Testing

### PT-001: Response Time Under Normal Load
**Objective:** Verify response times meet requirements

**Steps:**
1. Execute 100 sequential getCurrentUser queries
2. Measure average response time
3. Check 95th percentile response time

**Expected Results:**
- Average response time < 100ms
- 95th percentile response time < 100ms

### PT-002: Response Time Under High Load
**Objective:** Verify response times under concurrent load

**Steps:**
1. Execute 50 concurrent getCurrentUser queries
2. Measure response times
3. Check for timeouts or errors

**Expected Results:**
- All requests complete successfully
- Response times within acceptable range
- No service degradation

## Security Testing

### ST-001: Unauthorized Access to Organization Data
**Objective:** Verify that users cannot access other users' organization data

**Steps:**
1. Authenticate as User A
2. Attempt to retrieve User B's profile with organization details
3. Observe response

**Expected Results:**
- Appropriate authorization error
- No access to User B's organization data

### ST-002: SQL Injection Attempts
**Objective:** Verify protection against injection attacks

**Steps:**
1. Execute queries with malicious input in filter parameters
2. Observe response

**Expected Results:**
- Appropriate validation errors
- No unauthorized data access
- No service crashes

## Rollback Testing

### RT-001: Service Restart with Active Connections
**Objective:** Verify proper handling of service restarts

**Steps:**
1. Execute long-running queries
2. Restart organization service during query execution
3. Observe client behavior

**Expected Results:**
- Clients receive appropriate error responses
- No data corruption
- Service restarts successfully

## Monitoring and Logging Verification

### ML-001: Log Message Format
**Objective:** Verify that log messages are properly formatted

**Steps:**
1. Execute various operations
2. Check service logs
3. Verify log message format and content

**Expected Results:**
- Log messages include relevant identifiers
- Appropriate log levels used (debug, info, warning, error)
- No sensitive information logged

### ML-002: Metric Collection
**Objective:** Verify that metrics are collected properly

**Steps:**
1. Execute various operations
2. Check metric collection system
3. Verify metrics are recorded

**Expected Results:**
- Response time metrics recorded
- Error rate metrics recorded
- Success rate metrics recorded

## Cleanup
After testing, clean up test data:
1. Delete test organizations from MongoDB
2. Remove test user metadata from SuperTokens
3. Reset any modified configurations

## Test Data Requirements
- Minimum 3 test users with different roles
- Minimum 2 test organizations
- Sample data for edge case testing
- Backup of production-like data for restoration

## Test Success Criteria
1. All functional test cases pass (TC-001 through TC-007)
2. All edge case tests pass (EC-001 through EC-003)
3. Performance requirements met (PT-001 and PT-002)
4. Security requirements met (ST-001 and ST-002)
5. No critical or high severity issues found
6. All log messages appropriate and informative
7. All metrics collected correctly

## Test Failure Procedures
If any test fails:
1. Document the failure with detailed steps to reproduce
2. Capture relevant log messages
3. Identify the root cause if possible
4. Create a bug report with priority level
5. Determine if failure blocks release

## Test Environment Restoration
After testing:
1. Restore services to normal operation
2. Clean up test data
3. Verify production data integrity
4. Confirm all services functioning normally
