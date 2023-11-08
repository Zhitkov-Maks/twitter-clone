from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud.tweet import (
    add_like_in_db,
    add_tweet_in_db,
    delete_like_in_db,
    delete_tweet_by_id,
    get_tweet_by_id,
)
from crud.user import get_user_by_api_key
from models.db_conf import get_async_session
from models.model import Tweet
from models.model import User
from schemas.tweet_schema import ListTweetSchema, ReturnAddTweetSchema, AddTweetSchema, SuccessSchema
from service import tweet_constructor

route_tw = APIRouter(prefix="/api")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@route_tw.get(
    "/tweets",
    status_code=status.HTTP_200_OK,
    response_model=ListTweetSchema,
)
async def get_all_tweets(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Get list tweets."""
    user = await get_user_by_api_key(session, api_key)
    return await tweet_constructor(session, user.id)


@route_tw.post(
    "/tweets",
    status_code=status.HTTP_201_CREATED,
    response_model=ReturnAddTweetSchema,
)
async def add_tweets(
    tweet_in: AddTweetSchema,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, int]:
    """Added "tweet."""
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: int = await add_tweet_in_db(session, user, tweet_in)
    return {"result": True, "tweet_id": tweet}


@route_tw.delete(
    "/tweets/{tweet_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema,
)
async def delete_tweet(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Removed tweet."""
    user: User = await get_user_by_api_key(session, api_key)
    tweet: Tweet = await get_tweet_by_id(session, tweet_id)

    if tweet.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "result": False,
                "error_type": "Forbidden",
                "error_message": "You can not delete this tweet",
            },
        )

    await delete_tweet_by_id(session, tweet)
    return {"result": True}


@route_tw.post(
    "/tweets/{tweet_id}/likes",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema,
)
async def add_likes(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Added likes."""
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: Tweet | None = await get_tweet_by_id(session, tweet_id)
    await add_like_in_db(session, tweet, user)
    return {"result": True}


@route_tw.delete(
    "/tweets/{tweet_id}/likes",
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema,
)
async def delete_likes(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Removed likes."""
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: Tweet | None = await get_tweet_by_id(session, tweet_id)

    await delete_like_in_db(session, tweet, user)
    return {"result": True}
