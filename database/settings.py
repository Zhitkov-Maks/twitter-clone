from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from database.config import DB_USER, DB_PASS, DB_NAME

DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@db/{DB_NAME}"
Base = declarative_base()


engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
