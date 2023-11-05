import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from main import app
from models import User, Tweet
from models.db_conf import get_async_session, Base

DATABASE_URL_TEST: str = (
    f"postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
)

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    bind=engine_test, autoflush=False, autocommit=False, expire_on_commit=False
)

Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


async def insert_objects_users(
        async_session: async_sessionmaker[AsyncSession]) -> None:
    async with (async_session() as session):
        async with session.begin():
            usr_alex = User(name="Alex", api_key="test")
            usr_maks = User(name="Maks", api_key="qwerty")
            usr_polina = User(name="Polina", api_key="test_2")
            usr_anna = User(name="Anna", api_key="qwerty_2")
            session.add_all([usr_alex, usr_maks, usr_polina, usr_anna])

            usr_alex.followed.append(usr_maks)
            usr_maks.followed.append(usr_polina)
            usr_anna.followed.append(usr_alex)

            tweet_1 = Tweet(tweet_data="Tweet content",
                            tweet_media_ids=["image.png"])
            tweet_2 = Tweet(
                tweet_data="Tweet content another",
                tweet_media_ids=["image.png"]
            )

            usr_alex.tweets.append(tweet_1)
            usr_polina.tweets.append(tweet_2)
            usr_maks.likes.append(tweet_1)
            usr_anna.likes.append(tweet_2)

            session.add_all(
                usr_alex.followed
                + usr_maks.followed
                + usr_anna.followed
                + usr_alex.tweets
                + usr_polina.tweets
                + usr_maks.likes
                + usr_anna.likes
            )
            await session.commit()


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await insert_objects_users(async_session_maker)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
