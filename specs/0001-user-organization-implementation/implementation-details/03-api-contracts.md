# API Contracts: User-Organization Relationship Management

## Overview
This document defines the API contracts for the User-Organization Relationship Management feature, including GraphQL schemas, query structures, and response formats.

## GraphQL Schema Extensions

### Auth Service Schema Extension
**Location:** `backend/modules/auth/graphql/schema.graphql`

```graphql
directive @oneOf on INPUT_OBJECT

schema @link(url: "https://specs.apollo.dev/federation/v2.7", import: ["@key", "@shareable"]) {
  query: Query
  mutation: Mutation
}

type User @key(fields: "id") {
  id: UUID!
  firstName: String
  lastName: String
  email: String!
  timeJoined: DateTime!
  organizationId: UUID @shareable
  invited: Boolean!
  inviteStatus: InviteStatus!
  inviterName: String
  roles: [Role!]
}

type UserGraphQLResponse {
  """The list of items in this pagination window."""
  items(filterBy: FilterBy = null, sortBy: SortBy = null, offset: Int! = 0, limit: Int): [User!]

  """Total number of items in the filtered dataset."""
  count(filterBy: FilterBy = null): Int!
}

extend type Query {
  """Returns all Users"""
  users: UserGraphQLResponse!
}

input UpdateUserInput {
  id: UUID!
  firstName: String
  lastName: String
  email: EmailAddress
  currentPassword: String
  newPassword: String
  invited: Boolean
  inviteStatus: InviteStatus
  inviterName: String
  role: Role
  organizationId: UUID
}
```

### Organization Service Schema Extension
**Location:** `backend/modules/organization/graphql/schema.graphql`

```graphql
directive @oneOf on INPUT_OBJECT

schema @link(url: "https://specs.apollo.dev/federation/v2.7", import: ["@key", "@shareable"]) {
  query: Query
  mutation: Mutation
}

type User @key(fields: "id") {
  id: UUID!
  organizationId: UUID @shareable
  organization: Organization
}

type Organization @key(fields: "id") {
  id: UUID!
  name: String!
  address: String!
  city: String!
  country: CountryCodes!
  metaData: OrganizationMetaData!
}

extend type Query {
  """Returns all Organizations"""
  organizations: OrganizationGraphQLResponse!
}

extend type Mutation {
  """
  Creates multiple organizations and associates them with the current user
  """
  createOrganizations(organizations: [InputOrganization!]!): [Organization!]!
}
```

## Core Queries

### Get Current User with Organization
This is the primary query that was experiencing the "list index out of range" error.

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

**Variables:**
```json
{
  "id": "12345678-1234-5678-1234-567812345678"
}
```

**Expected Response (Success):**
```json
{
  "data": {
    "users": {
      "items": [
        {
          "id": "12345678-1234-5678-1234-567812345678",
          "firstName": "John",
          "lastName": "Doe",
          "email": "john.doe@example.com",
          "roles": ["OWNER"],
          "organization": {
            "id": "87654321-4321-8765-4321-876543218765",
            "name": "Example Organization",
            "address": "123 Main St",
            "city": "Example City",
            "country": "CHE",
            "metaData": {
              "stakeholders": ["BUILDING_DATA_OWNERS", "DESIGN_PROFESSIONALS"]
            }
          },
          "timeJoined": "2023-01-01T00:00:00Z"
        }
      ]
    }
  }
}
```

**Expected Response (Missing Organization):**
```json
{
  "data": {
    "users": {
      "items": [
        {
          "id": "12345678-1234-5678-1234-567812345678",
          "firstName": "John",
          "lastName": "Doe",
          "email": "john.doe@example.com",
          "roles": ["MEMBER"],
          "organization": null,
          "timeJoined": "2023-01-01T00:00:00Z"
        }
      ]
    }
  }
}
```

**Expected Response (Error Case - Fixed):**
```json
{
  "data": {
    "users": {
      "items": [
        {
          "id": "12345678-1234-5678-1234-567812345678",
          "firstName": "John",
          "lastName": "Doe",
          "email": "john.doe@example.com",
          "roles": ["OWNER"],
          "organization": null,
          "timeJoined": "2023-01-01T00:00:00Z"
        }
      ]
    }
  },
  "errors": [
    {
      "message": "list index out of range",
      "path": ["users", "items", 0],
      "extensions": {
        "service": "organization"
      }
    }
  ]
}
```

*Note: After implementation, the error should no longer occur, and the organization field should be null instead.*

## Mutations

### Create Organization
```graphql
mutation createOrganization($input: [InputOrganization!]!) {
  createOrganizations(organizations: $input) {
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

**Variables:**
```json
{
  "input": [
    {
      "name": "New Organization",
      "address": "456 New Street",
      "city": "New City",
      "country": "USA",
      "metaData": {
        "stakeholders": ["CONSTRUCTION_COMPANIES"]
      }
    }
  ]
}
```

**Expected Response:**
```json
{
  "data": {
    "createOrganizations": [
      {
        "id": "11111111-2222-3333-4444-555555555555",
        "name": "New Organization",
        "address": "456 New Street",
        "city": "New City",
        "country": "USA",
        "metaData": {
          "stakeholders": ["CONSTRUCTION_COMPANIES"]
        }
      }
    ]
  }
}
```

## Error Responses

### ERR-1: List Index Out of Range (Before Fix)
**HTTP Status:** 200 (GraphQL always returns 200)
**Response Body:**
```json
{
  "data": {
    "users": {
      "items": []
    }
  },
  "errors": [
    {
      "message": "list index out of range",
      "path": ["users", "items", 0],
      "extensions": {
        "service": "organization"
      }
    }
  ]
}
```

### ERR-2: Organization Not Found (After Fix)
**HTTP Status:** 200
**Response Body:**
```json
{
  "data": {
    "users": {
      "items": [
        {
          "id": "12345678-1234-5678-1234-567812345678",
          "firstName": "John",
          "lastName": "Doe",
          "email": "john.doe@example.com",
          "roles": ["MEMBER"],
          "organization": null,
          "timeJoined": "2023-01-01T00:00:00Z"
        }
      ]
    }
  }
}
```

### ERR-3: Cross-Service Communication Failure
**HTTP Status:** 200
**Response Body:**
```json
{
  "data": null,
  "errors": [
    {
      "message": "Could not receive data from router URL. Got HTTP 500",
      "path": ["users"],
      "extensions": {
        "service": "organization"
      }
    }
  ]
}
```

## Field Definitions

### User Fields
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| id | UUID! | Unique identifier | Yes |
| firstName | String | User's first name | No |
| lastName | String | User's last name | No |
| email | String! | User's email address | Yes |
| timeJoined | DateTime! | When user joined | Yes |
| organizationId | UUID | Reference to organization | No |
| organization | Organization | Organization details | No |
| roles | [Role!] | User's roles | No |

### Organization Fields
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| id | UUID! | Unique identifier | Yes |
| name | String! | Organization name | Yes |
| address | String! | Street address | Yes |
| city | String! | City | Yes |
| country | CountryCodes! | Country (ISO 3166-1 alpha-3) | Yes |
| metaData | OrganizationMetaData! | Additional metadata | Yes |

### OrganizationMetaData Fields
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| stakeholders | [StakeholderEnum!]! | Organization stakeholders | Yes |

## Input Types

### InputOrganization
| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| id | UUID! | Unique identifier | No | Generated |
| name | String! | Organization name | Yes | - |
| address | String! | Street address | Yes | - |
| city | String! | City | Yes | - |
| country | CountryCodes! | Country | Yes | - |
| metaData | InputOrganizationMetaData! | Metadata | No | Empty |

### FilterBy
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| equal | JSON | Exact match filter | No |
| contains | JSON | Contains filter | No |
| startsWith | JSON | Starts with filter | No |
| endsWith | JSON | Ends with filter | No |
| gt | JSON | Greater than filter | No |
| gte | JSON | Greater than or equal filter | No |
| lt | JSON | Less than filter | No |
| lte | JSON | Less than or equal filter | No |
| notEqual | JSON | Not equal filter | No |
| isTrue | Boolean | Boolean filter | No |
| in | JSON | In list filter | No |

## Enums

### CountryCodes
ISO 3166-1 alpha-3 country codes (partial list):
- AFG, ALA, ALB, DZA, ASM, AND, AGO, AIA, ATA, ATG, ARG, ARM, ABW, AUS, AUT, AZE, BHS, BHR, BGD, BRB, BLR, BEL, BLZ, BEN, BMU, BTN, BOL, BES, BIH, BWA, BVT, BRA, IOT, BRN, BGR, BFA, BDI, CPV, KHM, CMR, CAN, CYM, CAF, TCD, CHL, CHN, CXR, CCK, COL, COM, COG, COD, COK, CRI, CIV, HRV, CUB, CUW, CYP, CZE, DNK, DJI, DMA, DOM, ECU, EGY, SLV, GNQ, ERI, EST, SWZ, ETH, FLK, FRO, FJI, FIN, FRA, GUF, PYF, ATF, GAB, GMB, GEO, DEU, GHA, GIB, GRC, GRL, GRD, GLP, GUM, GTM, GGY, GIN, GNB, GUY, HTI, HMD, VAT, HND, HKG, HUN, ISL, IND, IDN, IRN, IRQ, IRL, ISR, ITA, JAM, JPN, JEY, JOR, KAZ, KEN, KIR, PRK, KOR, KWT, KGZ, LAO, LVA, LBN, LSO, LBR, LBY, LIE, LTU, LUX, MAC, MDG, MWI, MYS, MDV, MLI, MLT, MHL, MTQ, MRT, MUS, MYT, MEX, FSM, MDA, MCO, MNG, MNE, MSR, MAR, MOZ, MMR, NAM, NRU, NPL, NLD, NCL, NZL, NIC, NER, NGA, NIU, NFK, MNP, NOR, OMN, PAK, PLW, PSE, PAN, PNG, PRY, PER, PHL, PCN, POL, PRT, PRI, QAT, REU, ROU, RUS, RWA, RYU, SBH, SHN, KNA, LCA, MAF, SPM, VCT, WSM, SMR, STP, SAU, SEN, SRB, SYC, SLE, SGP, SXM, SVK, SVN, SLB, SOM, ZAF, SGS, SSD, ESP, LKA, SDN, SUR, SJM, SWE, CHE, SYR, TWN, TJK, TZA, THA, TLS, TGO, TKL, TON, TTO, TUN, TUR, TKM, TCA, TUV, UGA, UKR, ARE, GBR, UMI, USA, URY, UZB, VUT, VEN, VNM, VGB, VIR, WLF, ESH, YEM, ZMB, ZWE

### StakeholderEnum
- BUILDING_DATA_OWNERS
- DESIGN_PROFESSIONALS
- LCA_TOOL_DEVELOPERS
- LCA_CONSULTANTS
- BUILDING_USERS
- CIVIL_SOCIETY
- CLIENTS_INVESTORS_OWNERS
- CONSTRUCTION_COMPANIES
- CONSTRUCTION_PRODUCT_MANUFACTURERS
- FACILITY_MANAGERS
- FINANCIAL_SERVICE_PROVIDERS
- FUNDING_SYSTEM_DEVELOPERS
- STANDARDIZATION_BODIES
- MEDIA_REPRESENTATIVES
- POLICY_LAW_MAKERS
- PRODUCT_LCA_DATABASE_DEVELOPERS
- PRODUCT_LCA_EPD_DATA_DEVELOPERS
- RESEARCHERS
- SURVEYORS_VALUATION_PROFESSIONALS
- SUSTAINABILITY_ASSESSMENT_SYSTEM_DEVELOPERS
- SUSTAINABILITY_AUDITORS
- ESG_CONSULTANTS

### Role
- OWNER
- MEMBER
- ADMIN

## Validation Rules

### Query Validation
1. User ID must be a valid UUID format
2. Filter parameters must match available fields
3. Limit parameter must be between 1 and 1000

### Mutation Validation
1. Organization name is required and must be 1-255 characters
2. Address is required and must be 1-500 characters
3. City is required and must be 1-100 characters
4. Country must be a valid CountryCodes enum value
5. Stakeholders must be valid StakeholderEnum values

## Rate Limiting

### Query Limits
- `getCurrentUser`: 1000 requests per hour per IP
- `users`: 100 requests per hour per IP

### Mutation Limits
- `createOrganizations`: 10 requests per hour per user

## Versioning

### Schema Version
Current version: v1.0.0

### Backward Compatibility
- All existing queries will continue to work
- New optional fields may be added
- Required fields will not be removed or made optional

## Deprecation Policy

### Field Deprecation
Deprecated fields will be marked with `@deprecated(reason: "...")` directive and maintained for 6 months.

### Schema Deprecation
Major schema changes will be introduced as new schema versions with a migration period of 12 months.

## Monitoring and Metrics

### Key Metrics
1. Query response time (target: <100ms for 95% of requests)
2. Error rate (target: <0.1%)
3. Success rate for organization resolution (target: >99.9%)

### Tracing
All requests will include tracing headers for performance monitoring:
- `X-Request-ID`: Unique request identifier
- `X-Trace-ID`: Distributed tracing identifier

## Security Considerations

### Authentication
All queries and mutations require valid authentication tokens.

### Authorization
- Users can only access their own organization information
- Organization details are only visible to members of that organization
- OWNER role required for organization modifications

### Data Protection
- Personal information is protected according to GDPR
- Organization metadata is only accessible to authorized users
- Audit logs track all access to user-organization relationships
