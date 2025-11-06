import asyncio
import logging
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from models import DBOrganization

logger = logging.getLogger("main")


class OrganizationCache:
    def __init__(self, cache_size: int = 5000):
        self.cache_size = cache_size
        self.cache: dict[UUID, "DBOrganization"] = {}
        self.lock = asyncio.Lock()
        self._reload_task = None

    async def load_all(self):
        """Load all organizations into cache"""
        from models import DBOrganization

        async with self.lock:
            try:
                organizations = await DBOrganization.find_all().to_list()
                logger.info(f"Loading {len(organizations)} organizations into cache")

                for org in organizations:
                    self.cache[org.id] = org

                logger.info(f"Successfully loaded {len(self.cache)} organizations")
            except Exception as e:
                logger.error(f"Failed to load organizations into cache: {e}")
                import traceback

                traceback.print_exc()

    async def _periodic_reload(self):
        """Reload all organizations every 12 hours"""
        while True:
            try:
                await asyncio.sleep(12 * 60 * 60)  # 12 hours in seconds
                logger.info("Performing periodic organization cache reload (12 hour interval)")
                await self.load_all()
            except Exception as e:
                logger.error(f"Error during periodic cache reload: {e}")
                import traceback

                traceback.print_exc()

    def start_periodic_reload(self):
        """Start the periodic reload task"""
        if self._reload_task is None:
            self._reload_task = asyncio.create_task(self._periodic_reload())
            logger.info("Started periodic organization cache reload task")

    async def get_organization(self, id: UUID) -> Optional["DBOrganization"]:
        """Get a single organization by ID"""
        async with self.lock:
            return self.cache.get(id)

    async def get_all_organizations(self) -> list["DBOrganization"]:
        """Get all cached organizations"""
        async with self.lock:
            return list(self.cache.values())

    async def reload_organization(self, id: UUID):
        """Reload a single organization from database"""
        from models import DBOrganization

        async with self.lock:
            try:
                org = await DBOrganization.get(id)
                if org:
                    self.cache[id] = org
                    logger.debug(f"Reloaded organization {id} into cache")
                else:
                    # Organization was deleted, remove from cache
                    self.cache.pop(id, None)
                    logger.debug(f"Removed deleted organization {id} from cache")
            except Exception as e:
                logger.error(f"Failed to reload organization {id}: {e}")

    async def remove_organization(self, org_id: UUID):
        """Remove organization from cache"""
        async with self.lock:
            self.cache.pop(org_id, None)
            logger.debug(f"Removed organization {org_id} from cache")

    async def add_organization(self, org: "DBOrganization"):
        """Add a new organization to cache"""
        async with self.lock:
            self.cache[org.id] = org
            logger.debug(f"Added organization {org.id} to cache")


# Global cache instance - will be initialized in lifespan
_organization_cache: Optional[OrganizationCache] = None


def get_organization_cache() -> OrganizationCache:
    """Get the organization cache instance"""
    if _organization_cache is None:
        raise RuntimeError("OrganizationCache not initialized. Call init_organization_cache() first.")
    return _organization_cache


def init_organization_cache(cache_size: int = 15000) -> OrganizationCache:
    """Initialize the organization cache with the given database URL"""
    global _organization_cache
    _organization_cache = OrganizationCache(cache_size=cache_size)
    return _organization_cache
