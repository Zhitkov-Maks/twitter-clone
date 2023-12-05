"""Module for database query operations for working with users."""
from fastapi import HTTPException
from models.model import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from schemas.user_schema import AddUserSchema


async def get_full_user_data(session: AsyncSession, user: User):
    """Function to download complete user information.
    Returning the user with complete information."""
    stmt = (
        select(User)
        .options(joinedload(User.followed))
        .options(joinedload(User.follower))
        .options(joinedload(User.tweets))
        .filter(User.id == user.id)
    )
    return await session.scalar(stmt)


async def get_user_data_followed(session: AsyncSession, user_id):
    """Function for getting users subscribed to.
    Returning the user with complete information."""
    stmt = select(User).options(joinedload(User.followed)).filter(User.id == user_id)
    return await session.scalar(stmt)


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> User:
    """Function to get user by api-key."""
    stmt = select(User).where(User.api_key == api_key)
    user: User | None = await session.scalar(stmt)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": "User is not found.",
        },
    )


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    """Function to get user by ID."""
    user: User | None = await session.get(User, user_id)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": "User is not found.",
        },
    )


async def add_followed(session: AsyncSession, user_id, user_followed):
    """Add subscription."""
    user: User = await get_user_data_followed(session, user_id)
    try:
        user.followed.append(user_followed)
        session.add_all(user.followed)
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "Bad Request",
                "error_message": "You are already subscribed",
            },
        )


async def remove_followed(session: AsyncSession, user_id, user_followed):
    """Function for unsubscribing from a user."""
    user: User = await get_user_data_followed(session, user_id)
    try:
        user.followed.remove(user_followed)
        await session.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "result": False,
                "error_type": "Not Found",
                "error_message": "You are not following this user",
            },
        )


async def get_user_by_api_key_no_exception(
        session: AsyncSession, api_key: str
) -> bool:
    """Function to get user by api-key. Needed to check for api_key"""
    stmt = select(User).where(User.api_key == api_key)
    user: User | None = await session.scalar(stmt)
    if user is None:
        return True
    return False


async def add_user_in_db(session: AsyncSession, data_in: AddUserSchema):
    """The function adds a user to the database"""
    data = data_in.model_dump()
    existence_check = await get_user_by_api_key_no_exception(session, data["api_key"])
    if existence_check:
        user = User(**data)
        session.add(user)
        await session.commit()
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "result": False,
            "error_type": "UNAUTHORIZED",
            "error_message": "Api key already exists",
        },
    )
