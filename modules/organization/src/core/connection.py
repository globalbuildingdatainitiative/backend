from typing import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from .config import settings


def create_postgres_engine():
    return create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        future=True,
        pool_size=settings.POSTGRES_POOL_SIZE,
        max_overflow=settings.POSTGRES_MAX_OVERFLOW,
        connect_args={"ssl": settings.POSTGRES_SSL},
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    local_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=create_postgres_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with local_session() as session:
        yield session
