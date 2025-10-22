import logging

import strawberry
from strawberry import Info

# from core.context import get_user
from core.cache import user_cache
from core.context import MICROSERVICE_USER_ID

from logic import get_users
from models import GraphQLUser, FilterBy, SortBy, Role
logger = logging.getLogger("main")


@strawberry.type(name="UserGraphQLResponse")
class UserResponse:
    """Response type for user queries with pagination support"""

    def _get_cache_key(self, user_id: str, is_admin: bool, filter_by: FilterBy | None, sort_by: SortBy | None) -> str:
        """Generate a cache key for the current query parameters"""
        return f"{user_id}:{is_admin}:{filter_by}:{sort_by}"

    async def _fetch_users(
        self,
        info: Info,
        filter_by: FilterBy | None = None,
        sort_by: SortBy | None = None,
        limit: int | None = 50,
        offset: int = 0,
    ) -> tuple[list[GraphQLUser], int]:
        """Internal method to fetch users with caching"""
        # Initialize cache if not already done
        if not hasattr(self, "_cache"):
            self._cache = None
            self._cache_count = None
            self._cache_key = None

        user_id = info.context.get('user').id

        # Check if this is a microservice request
        if user_id == MICROSERVICE_USER_ID:
            logger.info(f"Microservice request detected (UUID: {user_id}). Treating as admin access.")
            is_admin = True
        else:
            # Regular user - fetch from cache
            user = await user_cache.get_user(user_id)
            
            # Handle case where user is not found in cache
            if user is None:
                logger.warning(f"User {user_id} not found in cache during query")
                return [], 0
                
            is_admin = Role.ADMIN in user.roles

        # Generate cache key (without limit/offset for count queries)
        cache_key = self._get_cache_key(user_id, is_admin, filter_by, sort_by)

        # Return cached result if available and cache key matches
        if self._cache is not None and self._cache_key == cache_key:
            logger.debug("Using cached user query result")
            if limit is not None:
                return self._cache[offset : offset + limit], self._cache_count
            return self._cache[offset:], self._cache_count

        # Fetch fresh data
        logger.debug("Fetching users from database")
        if is_admin:
            users, total_count = await get_users(filter_by, sort_by, limit=None, offset=0)
            logger.info(f"Got {len(users)} users as admin (total: {total_count})")
        else:
            # Add organization filter for non-admin users
            # Goal: only fetch users from the same organization as the requester
            filters = filter_by or FilterBy()

            # Ensure filters.equal exists and add organization filter
            if not filters.equal:
                filters.equal = {}
            filters.equal["organization_id"] = user.organization_id

            users, total_count = await get_users(filters, sort_by, limit=None, offset=0)
            logger.info(f"Got {len(users)} users (total: {total_count})")

        # Cache the full result
        self._cache = users
        self._cache_count = total_count
        self._cache_key = cache_key

        # Return paginated result with total count
        if limit is not None:
            return users[offset : offset + limit], total_count
        return users[offset:], total_count

    @strawberry.field(description="The list of users in this pagination window.")
    async def items(
        self,
        info: Info,
        filter_by: FilterBy | None = None,
        sort_by: SortBy | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[GraphQLUser]:
        users, _ = await self._fetch_users(info, filter_by, sort_by, limit, offset)
        return users

    @strawberry.field(description="Total number of users in the filtered dataset.")
    async def count(self, info: Info, filter_by: FilterBy | None = None) -> int:
        # Fetch users (will use cache if items was already called)
        _, total_count = await self._fetch_users(info, filter_by=filter_by, limit=None, offset=0)
        return total_count
