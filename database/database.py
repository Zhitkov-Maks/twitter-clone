import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool


DATABASE_URL: str = "postgresql+asyncpg://admin:admin@db/twitter_clone_db"
Base = declarative_base()


engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:

    async with async_session_maker() as session:
        yield session
