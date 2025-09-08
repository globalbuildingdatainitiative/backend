# Data Model: User-Organization Relationship Management

## Overview
This document defines the data models for the User-Organization Relationship Management feature, including entity relationships, field definitions, and serialization formats.

## Entity Relationship Diagram
```
+----------------+          +---------------------+
|     User       |          |   Organization      |
+----------------+          +---------------------+
| id (UUID)      |<---------| id (UUID)           |
| first_name     |    |     | name                |
| last_name      |    |     | address             |
| email          |    |     | city                |
| time_joined    |    |     | country             |
| organization_id|----+     | meta_data           |
| roles          |          +---------------------+
+----------------+
```

## Auth Service Data Models

### GraphQLUser
**Location:** `backend/modules/auth/src/models/user.py`

```python
@strawberry.federation.type(name="User", keys=["id"])
class GraphQLUser:
    id: UUID
    first_name: str | None
    last_name: str | None
    email: str
    time_joined: datetime
    organization_id: UUID | None = strawberry.field(directives=[Shareable()])
    invited: bool = False
    invite_status: InviteStatus = InviteStatus.NONE
    inviter_name: str | None = None
    roles: list[Role] | None
```

**Fields:**
- `id` (UUID): Unique identifier for the user
- `first_name` (str | None): User's first name
- `last_name` (str | None): User's last name
- `email` (str): User's email address
- `time_joined` (datetime): Timestamp when user joined
- `organization_id` (UUID | None): Reference to user's organization (shareable field)
- `invited` (bool): Whether user was invited
- `invite_status` (InviteStatus): Status of user invitation
- `inviter_name` (str | None): Name of user who sent invitation
- `roles` (list[Role] | None): User's roles in the system

**Directives:**
- `@key(fields: "id")`: Federation key for entity resolution
- `@shareable`: Indicates field can be resolved by multiple services

### SuperTokensUser
**Location:** `backend/modules/auth/src/models/user.py`

```python
class SuperTokensUser(BaseModel):
    id: UUID
    organization_id: UUID | None
```

**Fields:**
- `id` (UUID): Unique identifier for the user
- `organization_id` (UUID | None): Reference to user's organization in SuperTokens metadata

## Organization Service Data Models

### DBOrganization
**Location:** `backend/modules/organization/src/models/organization.py`

```python
class DBOrganization(OrganizationBase, Document):
    pass

class OrganizationBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    meta_data: OrganizationMetaDataModel = Field(default_factory=OrganizationMetaDataModel)
```

**Fields:**
- `id` (UUID): Unique identifier for the organization
- `name` (str): Organization name
- `address` (str): Organization street address
- `city` (str): Organization city
- `country` (CountryCodes): Organization country (ISO 3166-1 alpha-3 codes)
- `meta_data` (OrganizationMetaDataModel): Additional organization metadata

### GraphQLOrganization
**Location:** `backend/modules/organization/src/models/organization.py`

```python
@strawberry.federation.type(name="Organization", keys=["id"])
class GraphQLOrganization:
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    meta_data: OrganizationMetaData
```

**Fields:**
- `id` (UUID): Unique identifier for the organization
- `name` (str): Organization name
- `address` (str): Organization street address
- `city` (str): Organization city
- `country` (CountryCodes): Organization country (ISO 3166-1 alpha-3 codes)
- `meta_data` (OrganizationMetaData): Additional organization metadata

**Directives:**
- `@key(fields: "id")`: Federation key for entity resolution

### OrganizationMetaDataModel
**Location:** `backend/modules/organization/src/models/organization.py`

```python
class OrganizationMetaDataModel(BaseModel):
    stakeholders: List[StakeholderEnum] = Field(default_factory=list)
```

**Fields:**
- `stakeholders` (List[StakeholderEnum]): List of stakeholder types for the organization

### OrganizationMetaData (GraphQL)
**Location:** `backend/modules/organization/src/models/organization.py`

```python
@strawberry.type
class OrganizationMetaData:
    stakeholders: List[StakeholderEnum] = strawberry.field(default_factory=list)
```

**Fields:**
- `stakeholders` (List[StakeholderEnum]): List of stakeholder types for the organization

## Enumerations

### CountryCodes
**Location:** `backend/modules/organization/src/models/country_codes.py`

Enumeration of ISO 3166-1 alpha-3 country codes (e.g., CHE, USA, DEU)

### StakeholderEnum
**Location:** `backend/modules/organization/src/models/stakeholder.py`

Enumeration of stakeholder types:
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
**Location:** `backend/modules/auth/src/models/roles.py`

Enumeration of user roles:
- OWNER
- MEMBER
- ADMIN

## Input Models

### InputOrganization
**Location:** `backend/modules/organization/src/models/organization.py`

```python
@strawberry.input
class InputOrganization:
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    city: str
    country: CountryCodes
    meta_data: InputOrganizationMetaData = strawberry.field(default_factory=InputOrganizationMetaData)
```

### InputOrganizationMetaData
**Location:** `backend/modules/organization/src/models/organization.py`

```python
@strawberry.input
class InputOrganizationMetaData:
    stakeholders: List[StakeholderEnum] = strawberry.field(default_factory=list)
```

## Data Flow

### 1. Organization Creation Flow
1. Client sends `InputOrganization` data to Organization service
2. Organization service creates `DBOrganization` in MongoDB
3. Organization service verifies organization is queryable
4. Organization service updates user metadata in SuperTokens
5. Organization service assigns OWNER role to user

### 2. User Profile Retrieval Flow
1. Client requests user profile with organization details
2. Auth service provides user data including `organization_id`
3. Organization service resolves `organization` field using `organization_id`
4. Organization service queries MongoDB for organization data
5. Organization data is returned alongside user data

## Serialization Formats

### JSON Representation (API Response)
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

### MongoDB Document (Organization)
```json
{
  "_id": "87654321-4321-8765-4321-876543218765",
  "name": "Example Organization",
  "address": "123 Main St",
  "city": "Example City",
  "country": "CHE",
  "meta_data": {
    "stakeholders": ["BUILDING_DATA_OWNERS", "DESIGN_PROFESSIONALS"]
  }
}
```

### SuperTokens Metadata (User)
```json
{
  "organization_id": "87654321-4321-8765-4321-876543218765"
}
```

## Indexing Strategy

### MongoDB Indexes
1. **Primary Index**: `_id` (UUID) - Automatic
2. **Recommended Index**: `organization_id` in user metadata - For faster lookups

### GraphQL Federation Keys
1. **User**: `id` field - Used for entity resolution
2. **Organization**: `id` field - Used for entity resolution

## Validation Rules

### Organization Validation
- `name`: Required, max 255 characters
- `address`: Required, max 500 characters
- `city`: Required, max 100 characters
- `country`: Required, valid CountryCodes enum value
- `meta_data.stakeholders`: Optional, valid StakeholderEnum values

### User Validation
- `organization_id`: Optional UUID, must reference existing organization if provided

## Migration Considerations

### Backward Compatibility
- Existing users without organizations will have `null` organization_id
- Existing organizations will maintain their current structure
- New fields are optional to preserve backward compatibility

### Data Migration
- No migration required for existing data
- New organization metadata will be initialized with empty stakeholders list

## Performance Considerations

### Query Optimization
- Organization lookups by ID should use indexed queries
- User-organization joins should leverage GraphQL federation
- Caching strategies should be considered for frequently accessed organizations

### Memory Usage
- Organization objects should be lightweight to minimize memory footprint
- Lazy loading of organization details when not immediately needed
- Efficient serialization to reduce network overhead

## Security Considerations

### Data Protection
- User-organization relationships should respect privacy settings
- Organization metadata should be accessible only to authorized users
- Audit logging should track organization creation and modification

### Access Control
- Only organization owners should be able to modify organization details
- User roles should control access to organization data
- Proper authentication and authorization for all operations
