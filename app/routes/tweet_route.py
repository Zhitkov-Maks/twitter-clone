"""We describe routes for requests related to tweets."""
from typing import Dict

from starlette import status

from crud.tweet import (
    add_like_in_db,
    add_tweet_in_db,
    delete_like_in_db,
    delete_tweet_by_id,
    get_tweet_by_id,
)
from crud.user import get_user_by_api_key
from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from models.db_conf import get_async_session
from models.model import Tweet, User
from schemas.tweet_schema import (
    AddTweetSchema,
    ListTweetSchema,
    ReturnAddTweetSchema,
    SuccessSchema,
    ErrorResponse,
)
from service import tweet_constructor
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

route_tw = APIRouter(prefix="/api")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@route_tw.get(
    "/tweets",
    status_code=status.HTTP_200_OK,
    response_model=ListTweetSchema,
    tags=["tweets"],
)
async def get_all_tweets(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Функция проверяет если пользователь в базе с пришедшим в header api_key, и если есть
    то отправляет на формирование списка твитов для отправки на frontend.

    :param api_key: Ключ для аутентификации пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращает словарь с нужными данными.
    """
    user = await get_user_by_api_key(session, api_key)
    return await tweet_constructor(session, user.id)


@route_tw.post(
    "/tweets",
    status_code=status.HTTP_201_CREATED,
    response_model=ReturnAddTweetSchema,
    responses={400: {"model": ErrorResponse}},
    tags=["tweets"]
)
async def add_tweets(
    tweet_in: AddTweetSchema,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, int] | JSONResponse:
    """
    Функция проверяет если пользователь в базе с пришедшим в header api_key, и если есть
    то отправляет на сохранение твита.

    :param tweet_in: Пришедшие с frontend данные для твита.
    :param api_key: Ключ для аутентификации пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращает словарь с идентификатором сохраненного твита.
    """
    user: User = await get_user_by_api_key(session, api_key)
    tweet: int = await add_tweet_in_db(session, user, tweet_in)
    return {"result": True, "tweet_id": tweet}


@route_tw.delete(
    "/tweets/{tweet_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema,
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["tweets"],
)
async def delete_tweet(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """
    Функция проверяет если пользователь в базе с пришедшим в header api_key, и если есть
    то отправляет на удаление твита.

    :param tweet_id: Идентификатор для удаления твита.
    :param api_key: Ключ для аутентификации пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращает словарь с результатом удаления твита.
    """

    user: User = await get_user_by_api_key(session, api_key)
    tweet: Tweet = await get_tweet_by_id(session, tweet_id)

    # Проверяем есть ли у пользователя право на удаление данного твита.
    if tweet.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "result": False,
                "error_type": "Forbidden",
                "error_message": "You do not have permission to delete this tweet",
            },
        )
    await delete_tweet_by_id(session, tweet)
    return {"result": True}


@route_tw.post(
    "/tweets/{tweet_id}/likes",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["tweets"],
)
async def add_likes(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool] | JSONResponse:
    """
    Функция проверяет если пользователь в базе с пришедшим в header api_key,
    есть ли твит с пришедшим идентификатором и если есть
    то отправляем на добавление лайка к нужному твиту.

    :param tweet_id: Идентификатор твита к которому нужно добавить лайк.
    :param api_key: Ключ для аутентификации пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращает словарь с результатом добавления лайка.
    """

    user: User = await get_user_by_api_key(session, api_key)
    tweet: Tweet = await get_tweet_by_id(session, tweet_id)
    await add_like_in_db(session, tweet, user)
    return {"result": True}


@route_tw.delete(
    "/tweets/{tweet_id}/likes",
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema,
    responses={404: {"model": ErrorResponse}},
    tags=["tweets"],
)
async def delete_likes(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool] | JSONResponse:
    """
    Функция проверяет если пользователь в базе с пришедшим в header api_key,
    есть ли твит с пришедшим идентификатором и если есть
    то отправляем на добавление лайка к нужному твиту.

    :param tweet_id: Идентификатор твита к которому нужно удалить лайк.
    :param api_key: Ключ для аутентификации пользователя.
    :param session: Сессия для работы с бд.
    :return Dict: Возвращает словарь с результатом удаления лайка.
    """

    user: User = await get_user_by_api_key(session, api_key)
    tweet: Tweet = await get_tweet_by_id(session, tweet_id)
    await delete_like_in_db(session, tweet, user)
    return {"result": True}
