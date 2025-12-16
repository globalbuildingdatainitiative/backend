from datetime import datetime, timezone
import logging

import strawberry
from strawberry import Info

from core.cache import get_user_cache
from core.context import MICROSERVICE_USER_ID

from logic import get_users
from models import GraphQLUser, FilterBy, SortBy, Role, UserStatistics

logger = logging.getLogger("main")


@strawberry.type(name="UserGraphQLResponse")
class UserResponse:
    """Response type for user queries with pagination support"""

    def __init__(self):
        # Store query parameters from items() to reuse in count()
        self._items_filter_by: FilterBy | None = None
        self._items_sort_by: SortBy | None = None

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

        user_id = info.context.get("user").id

        # Check if this is a microservice request
        if user_id == MICROSERVICE_USER_ID:
            is_admin = True
        else:
            # Regular user - fetch from cache
            user_cache = get_user_cache()
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
            if limit is not None:
                return self._cache[offset : offset + limit], self._cache_count
            return self._cache[offset:], self._cache_count

        # Fetch fresh data
        if is_admin:
            users, total_count = await get_users(filter_by, sort_by, limit=None, offset=0)
        else:
            # Add organization filter for non-admin users
            # Goal: only fetch users from the same organization as the requester
            filters = filter_by or FilterBy()

            # Ensure filters.equal exists and add organization filter
            if not filters.equal:
                filters.equal = {}
            filters.equal["organization_id"] = user.organization_id

            users, total_count = await get_users(filters, sort_by, limit=None, offset=0)

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
        # Store parameters for use by count() method
        self._items_filter_by = filter_by
        self._items_sort_by = sort_by
        users, _ = await self._fetch_users(info, filter_by, sort_by, limit, offset)
        return users

    @strawberry.field(description="Total number of users in the filtered dataset.")
    async def count(self, info: Info, filter_by: FilterBy | None = None, sort_by: SortBy | None = None) -> int:
        # If filter_by/sort_by not provided, use the ones from items() call
        # This ensures count uses the same filters as items when called in the same query
        effective_filter_by = filter_by if filter_by is not None else self._items_filter_by
        effective_sort_by = sort_by if sort_by is not None else self._items_sort_by

        # Fetch users (will use cache if items was already called with same parameters)
        _, total_count = await self._fetch_users(
            info, filter_by=effective_filter_by, sort_by=effective_sort_by, limit=None, offset=0
        )
        return total_count

    @strawberry.field(
        description="Get statistics on user utilization, with number of connected users in the last 30, 60, and 90 days."
    )
    async def statistics(self, info: Info) -> UserStatistics:
        stats = UserStatistics(active_last_30_days=0, active_last_60_days=0, active_last_90_days=0)
        users = await self.items(info, limit=None, offset=0)
        now = datetime.now(timezone.utc)

        for user in users:
            if user.last_login is None:
                continue

            last_login = user.last_login
            if last_login.tzinfo is None:
                last_login = last_login.replace(tzinfo=timezone.utc)

            days_since_login = (now - last_login).days
            if days_since_login <= 30:
                stats.active_last_30_days += 1
            if days_since_login <= 60:
                stats.active_last_60_days += 1
            if days_since_login <= 90:
                stats.active_last_90_days += 1

        return stats
