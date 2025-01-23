from enum import Enum

import strawberry


@strawberry.enum
class Role(Enum):
    OWNER = "owner"
    MEMBER = "member"
    ADMIN = "admin"


@strawberry.enum
class Permission(Enum):
    CONTRIBUTIONS_READ = "contributions::read"
    CONTRIBUTIONS_CREATE = "contributions::create"
    CONTRIBUTIONS_UPDATE = "contributions::update"
    CONTRIBUTIONS_DELETE = "contributions::delete"
    MEMBERS_READ = "members::read"
    MEMBERS_CREATE = "members::create"
    MEMBERS_UPDATE = "members::update"
    MEMBERS_DELETE = "members::delete"
    ORGANIZATIONS_CREATE = "organizations::create"
    ORGANIZATIONS_READ = "organizations::read"
    ORGANIZATIONS_UPDATE = "organizations::update"
    ORGANIZATIONS_DELETE = "organizations::delete"


@strawberry.type
class RolePermission:
    name: Role
    permissions: list[Permission]
