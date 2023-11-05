from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from models.model import User


async def get_full_user_data(session: AsyncSession, user: User) -> User:
    """
    Function to download complete user information.

    :param session: AsyncSession
    :param user: User
    """
    stmt = (
        select(User).
        options(joinedload(User.followed)).
        options(joinedload(User.follower)).
        options(joinedload(User.tweets)).
        filter(User.id == user.id)
    )
    return await session.scalar(stmt)


async def get_user_data_followed(session: AsyncSession, user_id) -> User:
    """
    Function for getting app_users subscribed to.

    :param session: AsyncSession
    :param user_id: User's ID
    """
    stmt = (
        select(User).options(joinedload(User.followed)).
        filter(User.id == user_id)
    )
    return await session.scalar(stmt)


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> User:
    """
    Function to get user by api-key.

    :param session: AsyncSession
    :param api_key: User's api-key
    """
    stmt = select(User).where(User.api_key == api_key)
    user: User | None = await session.scalar(stmt)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            'result': False,
            'error_type': 'Not Found',
            'error_message': 'User is not found.'
        },
    )


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    """
    Function to get user by ID.

    :param session
    :param user_id
    """
    user: User | None = await session.get(User, user_id)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            'result': False,
            'error_type': 'Not Found',
            'error_message': 'User is not found.'
        },
    )


async def add_followed(session: AsyncSession, user_id, user_followed):
    """
    Add subscription.

    :param session
    :param user_id
    :param user_followed
    """
    user = await get_user_data_followed(session, user_id)
    try:
        user.followed.append(user_followed)
        session.add_all(user.followed)
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'result': False,
                'error_type': 'Bad Request',
                'error_message': 'You are already subscribed'
            },
        )


async def remove_followed(session: AsyncSession, user_id, user_followed):
    """
    Function for unsubscribing from a user.

    :param session
    :param user_followed
    :param user_id
    """
    user = await get_user_data_followed(session, user_id)
    try:
        user.followed.remove(user_followed)
        await session.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'result': False,
                'error_type': 'Not Found',
                'error_message': 'You are not following this user'
            }
        )
