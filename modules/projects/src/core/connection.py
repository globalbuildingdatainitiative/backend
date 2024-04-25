import logging

from core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)


def create_mongo_client() -> AsyncIOMotorClient:
    """Create a new client to the Mongo database"""

    client = AsyncIOMotorClient(settings.MONGO_URI.__str__(), uuidRepresentation="standard")
    return client


def get_database() -> AsyncIOMotorDatabase:
    client = create_mongo_client()
    return client[settings.MONGO_DB]


@retry(
    stop=stop_after_attempt(60 * 5),
    wait=wait_fixed(1),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def health_check_mongo():
    try:
        db = get_database()
        response = await db.command("ping")
        logger.info(f"Got response from ping: {response}")
        if not response.get("ok"):
            raise ConnectionError
    except Exception as e:
        logger.error(e)
        raise e
