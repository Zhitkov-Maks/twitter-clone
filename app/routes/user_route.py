"""We describe routes for requests related to users."""
from typing import Dict

from starlette.responses import JSONResponse

from crud.user import (
    add_followed,
    get_user_by_api_key,
    get_user_by_id,
    remove_followed,
)
from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from models.db_conf import get_async_session
from models.model import User
from schemas.tweet_schema import SuccessSchema, ErrorResponse
from schemas.user_schema import ReturnUserSchema
from service import get_user_info
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

route_us = APIRouter(prefix="/api/users")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@route_us.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema,
    responses={404: {"model": ErrorResponse}},
    tags=["users"]
)
async def get_user_info_by_api_key(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Получение информации о текущем пользователе, по его api_key.

    :param api_key: Ключ для аутентификации пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращаем словарь с нужной информацией. Если пользователя не найдено
    пробрасываем исключение.
    """

    user: User = await get_user_by_api_key(session, api_key)
    return await get_user_info(session, user)


@route_us.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    tags=["users"],
)
async def get_user_info_by_id(
    user_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> dict | JSONResponse:
    """
    Функция проверяет есть ли пользователь с пришедшим api_key,
    если да то проверяет есть ли пользователь с пришедшим ID, если да то
    возвращает информацию о пользователе который нас интересует. В случае если где-то
    мы не сможем найти пользователя будет проброшено исключение.

    :param user_id: ID пользователя о котором нужно собрать информацию.
    :param api_key: Ключ для аутентификации текущего пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращаем в случае успеха словарь с информацией о пользователе.
    """

    await get_user_by_api_key(session, api_key)

    search_user: User = await get_user_by_id(session, user_id)
    return await get_user_info(session, search_user)


@route_us.delete(
    "/{user_id}/follow",
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema,
    responses={404: {"model": ErrorResponse}},
    tags=["users"],
)
async def remove_follow(
    user_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool] | JSONResponse:
    """
    Функция проверяет есть ли пользователь с пришедшим api_key,
    если да то проверяет есть ли пользователь с пришедшим ID, если да то
    удаляет подписку от пользователя. В случае если где-то
    мы не сможем найти пользователя будет проброшено исключение.

    :param user_id: ID пользователя от которого нужно отписаться.
    :param api_key: Ключ для аутентификации текущего пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращаем в случае успеха словарь с результатом работы.
    """
    user: User = await get_user_by_api_key(session, api_key)

    user_followed: User = await get_user_by_id(session, user_id)
    await remove_followed(session, user.id, user_followed)
    return {"result": True}


@route_us.post(
    "/{user_id}/follow",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["users"],
)
async def add_follow(
    user_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool] | JSONResponse:
    """
    Функция проверяет есть ли пользователь с пришедшим api_key,
    если да то проверяет есть ли пользователь с пришедшим ID, если да то
    добавляет подписку. В случае если где-то
    мы не сможем найти пользователя будет проброшено исключение.

    :param user_id: ID пользователя от которого нужно отписаться.
    :param api_key: Ключ для аутентификации текущего пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращаем в случае успеха словарь с результатом работы.
    """

    user: User = await get_user_by_api_key(session, api_key)
    if user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "result": False,
                "error_type": "Bad request",
                "error_message": "You can't subscribe to yourself.",
            }
        )

    user_followed: User = await get_user_by_id(session, user_id)
    await add_followed(session, user.id, user_followed)
    return {"result": True}
