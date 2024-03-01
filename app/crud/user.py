"""Module for database query operations for working with users."""
from fastapi import HTTPException
from models.model import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status


async def get_full_user_data(session: AsyncSession, user: User) -> User | None:
    """
    Функция для получения полной информации о пользователе.

    :param session: Сессия для работы с бд.
    :param user: Пользователь для которого идет сбор информации.
    :return user: Возвращаем пользователя с нужными данными.
    """
    stmt = (
        select(User)
        .options(joinedload(User.followed))
        .options(joinedload(User.follower))
        .options(joinedload(User.tweets))
        .filter(User.id == user.id)
    )
    return await session.scalar(stmt)


async def get_user_data_followed(session: AsyncSession, user_id: int) -> User | None:
    """
    Функция для получения информации о пользователе с его подписками.

    :param session: Сессия для работы с бд.
    :param user_id: ID пользователя для которого идет сбор информации.
    :return user: Возвращаем пользователя с нужными данными.
    """
    stmt = select(User).options(joinedload(User.followed)).filter(User.id == user_id)
    return await session.scalar(stmt)


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> User:
    """
    Получение пользователя по его api_key.

    :param session: Сессия для работы с бд.
    :param api_key: Ключ для аутентификации пользователя.
    :return user: Если пользователь найден, то возвращаем пользователя,
    иначе пробрасываем исключение.
    """
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
    """
    Получение пользователя по его ID.

    :param session: Сессия для работы с бд.
    :param user_id: ID для аутентификации пользователя.
    :return user: Если пользователь найден, то возвращаем пользователя,
    иначе пробрасываем исключение.
    """
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


async def add_followed(
    session: AsyncSession,
    user_id: int,
    user_followed: User
) -> None:
    """
    Подписка на другого пользователя.

    :param session: Сессия для работы с бд.
    :param user_id: ID для аутентификации пользователя.
    :param user_followed: Пользователь на которого мы хотим подписаться.
    :return None: Ничего не возвращаем, если подписка уже была - пробрасываем исключение.
    """
    user: User | None = await get_user_data_followed(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "result": False,
                "error_type": "Not Found",
                "error_message": "User is not found.",
            },
        )

    try:
        user.followed.append(user_followed)
        session.add_all(user.followed)
        await session.commit()

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "Bad request",
                "error_message": "Yoy already subscribed this user",
            }
        )


async def remove_followed(
    session: AsyncSession,
    user_id: int,
    user_followed: User
) -> None:
    """
    Удаление подписки от пользователя.

    :param session: Сессия для работы с бд.
    :param user_id: ID для аутентификации пользователя.
    :param user_followed: Пользователь от которого мы хотим отписаться.
    :return None: Ничего не возвращаем, если подписки нет - пробрасываем исключение.
    """
    user: User | None = await get_user_data_followed(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "result": False,
                "error_type": "Not Found",
                "error_message": "User is not found.",
            },
        )

    try:
        user.followed.remove(user_followed)
        await session.commit()

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "result": False,
                "error_type": "Not Found",
                "error_message": "You are not following this user.",
            }
        )
