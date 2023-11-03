"""Работа с операциями CRUD"""
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from database.models import Tweet, likes_table, User, Image, followers
from schemas import AddTweetSchema


async def transform_image_id_in_image_url(
    session: AsyncSession, tweet_in: AddTweetSchema
):
    unpack = tweet_in.model_dump()
    media = await get_image_url(session, unpack["tweet_media_ids"])
    unpack["tweet_media_ids"] = list(media)
    return unpack


async def add_tweet_in_db(
    session: AsyncSession, user: User, tweet_in: AddTweetSchema
) -> int:
    user = await get_full_user_data(session, user)
    unpack = await transform_image_id_in_image_url(session, tweet_in)
    tweet = Tweet(**unpack)
    user.tweets.append(tweet), session.add_all(user.tweets)
    await session.commit()
    return tweet.tweet_id


async def get_all_tweet_followed(session: AsyncSession, user_id: int):
    stmt = (
        select(
            Tweet,
            func.count(likes_table.c.user_id).label("likes"),
        )
        .join(followers, (followers.c.followed_id == Tweet.user_id))
        .join(likes_table, (likes_table.c.tweet_id == Tweet.tweet_id), isouter=True)
        .where(followers.c.follower_id == user_id)
        .group_by(Tweet.tweet_id)
        .order_by(desc("likes"))
        .limit(25)
    )
    all_tweet = await session.scalars(stmt)
    return all_tweet.unique().all()


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet:
    tweet: Tweet | None = await session.get(Tweet, tweet_id)
    if tweet is not None:
        return tweet
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": f"Tweet is not found",
        },
    )


async def get_full_user_data(session: AsyncSession, user: User) -> User:
    stmt = (
        select(User)
        .options(joinedload(User.followed))
        .options(joinedload(User.follower))
        .options(joinedload(User.tweets))
        .filter(User.id == user.id)
    )
    user = await session.scalar(stmt)
    return user


async def get_user_data_followed(session: AsyncSession, user_id) -> User:
    stmt = select(User).options(joinedload(User.followed)).filter(User.id == user_id)
    user = await session.scalar(stmt)
    return user


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> User:
    stmt = select(User).where(User.api_key == api_key)
    user: User | None = await session.scalar(stmt)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": f"User is not found",
        },
    )


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user: User | None = await session.get(User, user_id)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": f"User is not found",
        },
    )


async def delete_tweet_by_id(session: AsyncSession, tweet: Tweet):
    await session.delete(tweet)
    await session.commit()


async def add_image_in_db(session: AsyncSession, url: str) -> int:
    img: Image = Image(url=url)
    session.add(img)
    await session.commit()
    return img.id


async def add_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    try:
        tweet.likes.append(user)
        session.add_all(tweet.likes)
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "Bad Request",
                "error_message": "You've already liked it",
            },
        )


async def delete_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    try:
        tweet.likes.remove(user)
        await session.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "Bad Request",
                "error_message": "You've already deleted it",
            },
        )


async def add_followed(session: AsyncSession, user_id, user_followed):
    try:
        user = await get_user_data_followed(session, user_id)
        user.followed.append(user_followed)
        session.add_all(user.followed)
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "Bad Request",
                "error_message": f"User has already been added",
            },
        )


async def remove_followed(session: AsyncSession, user_id, user_followed):
    try:
        user = await get_user_data_followed(session, user_id)
        user.followed.remove(user_followed)
        await session.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "Bad Request",
                "error_message": f"User has already been deleted",
            },
        )


async def get_image_url(session: AsyncSession, image_id_list: List[int]):
    stmt = select(Image.url).where(Image.id.in_(image_id_list))
    return await session.scalars(stmt)
