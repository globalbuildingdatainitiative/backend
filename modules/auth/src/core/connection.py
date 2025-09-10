from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings

def get_postgres_engine():
    return create_async_engine(str(settings.POSTGRES_URI))