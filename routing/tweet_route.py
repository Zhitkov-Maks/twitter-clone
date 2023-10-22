from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.crud import get_user_by_api_key, get_tweet_by_id, \
    delete_tweet_by_id, add_like_in_db, delete_like_in_db
from database.database import db_helper
from database.models import User, Tweet
from schemas import Message
from services import generate_error_message

router_tw = APIRouter(prefix="/api/tweets")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@router_tw.delete(
    "/{tweet_id}",
    status_code=status.HTTP_200_OK,
    responses={403: {"model": Message}}
)
async def delete_tweet(
        tweet_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet = await get_tweet_by_id(session, tweet_id)

    if tweet.user_id != user.id:
        return await generate_error_message(403, "Forbidden", "You can't delete this tweet")

    await delete_tweet_by_id(session, tweet)
    return {"result": True}


@router_tw.post(
    "/{tweet_id}/likes",
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": Message}}
)
async def add_likes(
        tweet_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet = await get_tweet_by_id(session, tweet_id)
    add_like: bool | None = await add_like_in_db(session, tweet, user.id)
    if add_like is None:
        return {"result": True}
    return await generate_error_message(409, "Conflict", "You've already liked it")


@router_tw.delete(
    "/{tweet_id}/likes",
    status_code=status.HTTP_200_OK,
    responses={400: {"model": Message}}
)
async def delete_likes(
        tweet_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: Tweet | None = await get_tweet_by_id(session, tweet_id)

    delete_like = await delete_like_in_db(session, tweet, user)
    if delete_like is None:
        return {"result": True}
    return await generate_error_message(409, "Conflict", "You've already delete it")
