from typing import Optional, List
from uuid import UUID
from sqlalchemy import create_engine, text
import asyncio
from models import GraphQLUser, InviteStatus, Role
from datetime import datetime


class UserCache:
    def __init__(self, db_url: str, cache_size: int = 15000):
        self.db_url = db_url
        self.cache_size = cache_size
        # Use a regular dict for the cache - no TTL per item
        self.cache: dict[UUID, GraphQLUser] = {}
        self.engine = create_engine(db_url)
        self.lock = asyncio.Lock()
        self._reload_task = None

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
                            pending_org_id=self._safe_uuid(row.metadata.get("pending_org_id")),
                            invited=row.metadata.get("invited") or False,
                            invite_status=InviteStatus(row.metadata.get("invite_status"))
                            if row.metadata.get("invite_status")
                            else InviteStatus.NONE,
                            inviter_name=row.metadata.get("inviter_name"),
                            roles=[Role(role) for role in (row.roles or [])],
                        )
                        self.cache[self._safe_uuid(row.user_id)] = user
                    except Exception as e:
                        print(f"Failed to load user {row.user_id}: {e}")
                        print(f"  Metadata: {row.metadata}")
                        print(f"  Roles: {row.roles}")
                        import traceback

                        traceback.print_exc()

    async def _periodic_reload(self):
        """Reload all users every 12 hours"""
        while True:
            try:
                await asyncio.sleep(12 * 60 * 60)  # 12 hours in seconds
                print("Performing periodic cache reload (12 hour interval)")
                await self.load_all()
            except Exception as e:
                print(f"Error during periodic cache reload: {e}")
                import traceback

                traceback.print_exc()

    def start_periodic_reload(self):
        """Start the periodic reload task"""
        if self._reload_task is None:
            self._reload_task = asyncio.create_task(self._periodic_reload())

    async def get_user(self, id: UUID | str) -> Optional[GraphQLUser]:
        async with self.lock:
            return self.cache.get(UUID(id) if isinstance(id, str) else id)

    async def get_all_users(self) -> List[GraphQLUser]:
        async with self.lock:
            users = list(self.cache.values())
            none_count = sum(1 for u in users if u is None)
            if none_count > 0:
                print(f"ERROR in get_all_users: {none_count} out of {len(users)} users are None!")
            print(f"get_all_users() returning {len(users)} users from cache")
            return users

    async def reload_user(self, id: UUID | str) -> Optional[GraphQLUser]:
        if isinstance(id, UUID):
            uuid_id = id
            id = str(id)
        if isinstance(id, str):
            uuid_id = UUID(id)

        async with self.lock:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM user_full_view WHERE user_id = :user_id"), {"user_id": id})
                row = result.fetchone()
                if row:
                    user = GraphQLUser(
                        id=UUID(row.user_id),
                        email=row.email,
                        time_joined=datetime.fromtimestamp(round(row.time_joined / 1000)),
                        first_name=row.metadata.get("first_name"),
                        last_name=row.metadata.get("last_name"),
                        organization_id=self._safe_uuid(row.metadata.get("organization_id")),
                        pending_org_id=self._safe_uuid(row.metadata.get("pending_org_id")),
                        invited=row.metadata.get("invited") or False,
                        invite_status=InviteStatus(row.metadata.get("invite_status"))
                        if row.metadata.get("invite_status")
                        else InviteStatus.NONE,
                        inviter_name=row.metadata.get("inviter_name"),
                        roles=[Role(role) for role in (row.roles or [])],
                    )
                    self.cache[UUID(row.user_id)] = user
                    return user
                else:
                    self.cache.pop(uuid_id, None)
                    return None

    async def remove_user(self, user_id: UUID):
        if not isinstance(user_id, UUID):
            user_id = UUID(user_id)
        async with self.lock:
            self.cache.pop(user_id, None)

    async def clear_cache(self):
        async with self.lock:
            self.cache.clear()


# Global cache instance - will be initialized in lifespan
_user_cache: Optional[UserCache] = None


def get_user_cache() -> UserCache:
    """Get the user cache instance"""
    if _user_cache is None:
        raise RuntimeError("UserCache not initialized. Call init_user_cache() first.")
    return _user_cache


def init_user_cache(db_url: str, cache_size: int = 15000) -> UserCache:
    """Initialize the user cache with the given database URL"""
    global _user_cache
    _user_cache = UserCache(db_url, cache_size)
    return _user_cache
