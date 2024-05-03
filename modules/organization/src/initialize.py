import asyncio
import logging

from core.connection import health_check_mongo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Initializing service")
    await health_check_mongo()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
