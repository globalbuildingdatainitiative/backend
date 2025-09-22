import asyncio
import logging

from core.auth import health_check_supertokens
from core.connection import get_or_create_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")


async def main() -> None:
    logger.info("Initializing service")
    await health_check_supertokens()
    await get_or_create_database()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
