from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.crud import (
    get_user_by_api_key,
    get_tweet_by_id,
    delete_tweet_by_id,
    add_like_in_db,
    delete_like_in_db,
    add_tweet_in_db,
)
from database.models import User, Tweet
from database.settings import get_async_session
from schemas import SuccessSchema, ReturnAddTweetSchema, AddTweetSchema, ListTweetSchema
from services import tweet_constructor

route_tw = APIRouter(prefix="/api")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@route_tw.get("/tweets", status_code=status.HTTP_200_OK, response_model=ListTweetSchema)
async def get_all_tweets(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
):
    user = await get_user_by_api_key(session, api_key)
    result = await tweet_constructor(session, user.id)
    return result


@route_tw.post(
    "/tweets",
    status_code=status.HTTP_201_CREATED,
    response_model=ReturnAddTweetSchema,
)
async def add_tweets(
    tweet_in: AddTweetSchema,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
):
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: int = await add_tweet_in_db(session, user, tweet_in)
    return {"result": True, "tweet_id": tweet}


@route_tw.delete(
    "/tweets/{tweet_id}", status_code=status.HTTP_200_OK, response_model=SuccessSchema
)
async def delete_tweet(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
):
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: Tweet = await get_tweet_by_id(session, tweet_id)

    if tweet.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "result": False,
                "error_type": "Forbidden",
                "error_message": f"You can't delete this tweet",
            },
        )

    await delete_tweet_by_id(session, tweet)
    return {"result": True}


@route_tw.post("/tweets/{tweet_id}/likes", status_code=status.HTTP_201_CREATED)
async def add_likes(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
):
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: Tweet | None = await get_tweet_by_id(session, tweet_id)
    await add_like_in_db(session, tweet, user)
    return {"result": True}


@route_tw.delete("/tweets/{tweet_id}/likes", status_code=status.HTTP_200_OK)
async def delete_likes(
    tweet_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
):
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: Tweet | None = await get_tweet_by_id(session, tweet_id)

    await delete_like_in_db(session, tweet, user)
    return {"result": True}
