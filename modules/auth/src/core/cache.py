import os
from typing import Optional, List
from uuid import UUID
from sqlalchemy import create_engine, text
from cachetools import TTLCache
import asyncio
from models import GraphQLUser, InviteStatus, Role
from datetime import datetime
class UserCache:
    def __init__(self, db_url: str, cache_size: int = 1000, ttl: int = 300):
        self.db_url = db_url
        self.cache_size = cache_size
        self.ttl = ttl
        # Use TTLCache for automatic expiration, with LRU eviction policy
        self.cache: TTLCache[UUID, GraphQLUser] = TTLCache(maxsize=cache_size, ttl=ttl)
        self.engine = create_engine(db_url)
        self.lock = asyncio.Lock()

    def _safe_uuid(self, value: str | None) -> UUID | None:
        """Convert string to UUID, returning None if value is None or empty."""
        return UUID(value) if value else None

    async def load_all(self):
        async with self.lock:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM user_full_view"))
                rows = result.all()
                print("Loading users into cache", len(rows))
                for row in rows:
                    try:
                        # todo: should we have generic from metadata?
                        user = GraphQLUser(
                            id=UUID(row.user_id),
                            email=row.email,
                            time_joined=datetime.fromtimestamp(round(row.time_joined / 1000)),
                            first_name=row.metadata.get("first_name"),
                            last_name=row.metadata.get("last_name"),
                            organization_id=self._safe_uuid(row.metadata.get("organization_id")),
                            pending_org_id=self._safe_uuid(row.metadata.get("pending_organization_id")),
                            invited=row.metadata.get("invited") or False,
                            invite_status=InviteStatus(row.metadata.get("invite_status"))
                            if row.metadata.get("invite_status")
                            else InviteStatus.NONE,
                            inviter_name=row.metadata.get("inviter_name"),
                            roles=[Role(role) for role in (row.roles or [])],
                        )
                        self.cache[UUID(row.user_id)] = user
                    except Exception as e:
                        print(f"Failed to load user {row.user_id}: {e}")
                        print(f"  Metadata: {row.metadata}")
                        print(f"  Roles: {row.roles}")
                        import traceback

                        traceback.print_exc()

    async def get_user(self, id: UUID) -> Optional[GraphQLUser]:
        async with self.lock:
            return self.cache.get(id)

    async def get_all_users(self) -> List[GraphQLUser]:
        async with self.lock:
            users = list(self.cache.values())
            none_count = sum(1 for u in users if u is None)
            if none_count > 0:
                print(f"ERROR in get_all_users: {none_count} out of {len(users)} users are None!")
            print(f"get_all_users() returning {len(users)} users from cache")
            return users

    async def reload_user(self, id: UUID):
        async with self.lock:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM user_full_view WHERE user_id = :user_id"), {"user_id": str(id)}
                )
                row = result.fetchone()
                if row:
                    user = GraphQLUser(
                        id=UUID(row.user_id),
                        email=row.email,
                        time_joined=datetime.fromtimestamp(round(row.time_joined / 1000)),
                        first_name=row.metadata.get("first_name"),
                        last_name=row.metadata.get("last_name"),
                        organization_id=self._safe_uuid(row.metadata.get("organization_id")),
                        pending_org_id=self._safe_uuid(row.metadata.get("pending_organization_id")),
                        invited=row.metadata.get("invited") or False,
                        invite_status=InviteStatus(row.metadata.get("invite_status"))
                        if row.metadata.get("invite_status")
                        else InviteStatus.NONE,
                        inviter_name=row.metadata.get("inviter_name"),
                        roles=[Role(role) for role in (row.roles or [])],
                    )
                    self.cache[UUID(row.user_id)] = user
                else:
                    self.cache.pop(id, None)

    async def remove_user(self, user_id: UUID):
        async with self.lock:
            self.cache.pop(user_id, None)


# Get database URL from environment variable
# WARNING: This is a sensitive operation, ensure the environment variable is set correctly

# Use LOCAL for development, fallback to regular for production/Docker
db_url = os.getenv("POSTGRESQL_CONNECTION_URI_LOCAL") or os.getenv("POSTGRESQL_CONNECTION_URI", "FAILURE")
# Singleton instance
user_cache = UserCache(db_url, cache_size=1000, ttl=300)
