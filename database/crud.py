"""Работа с операциями CRUD"""
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from starlette import status

from database.models import User, Tweet, Image, likes_table, followers
from schemas import AddTweetSchema


async def add_tweet_in_db(session: AsyncSession, user: User, tweet_in: AddTweetSchema) -> int:
    tweet = Tweet(**tweet_in.model_dump())
    user.tweets.append(tweet)
    session.add_all(user.tweets)
    await session.commit()
    return tweet.tweet_id


async def get_all_tweet_followed(session: AsyncSession, user_id: int):
    stmt = (select(Tweet, func.count(likes_table.c.user_id).label("likes"))
            .join(followers, (followers.c.followed_id == Tweet.user_id))
            .join(Tweet.likes)
            .where(followers.c.follower_id == user_id)
            .group_by(Tweet.tweet_id)
            .order_by(desc("likes")).limit(10))
    all_tweet = await session.scalars(stmt)
    return all_tweet.unique().all()


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet | None:
    tweet: Tweet | None = await session.get(Tweet, tweet_id)
    if tweet is not None:
        return tweet
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": f"Tweet is not found"
        }
    )


async def get_full_user_data(session: AsyncSession, user_id) -> User:
    stmt = (select(User)
            .options(joinedload(User.followed))
            .options(joinedload(User.follower))
            .options(joinedload(User.likes)).filter(User.id == user_id))
    user = await session.scalar(stmt)
    return user


async def get_user_data_followed(session: AsyncSession, user_id) -> User:
    stmt = (select(User)
            .options(joinedload(User.followed))
            .filter(User.id == user_id))
    user = await session.scalar(stmt)
    return user


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> User | None:
    stmt = select(User).where(User.api_key == api_key)
    user: User | None = await session.scalar(stmt)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": f"User is not found"
        }
    )


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    user: User | None = await session.get(User, user_id)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": f"User is not found"
        }
    )


async def delete_tweet_by_id(session: AsyncSession, tweet: Tweet):
    await session.delete(tweet)
    await session.commit()


async def add_image_in_db(session: AsyncSession, url: str) -> int:
    img: Image = Image(url=url)
    session.add(img)
    await session.commit()
    return img.id


async def check_likes(session: AsyncSession, tweet_id: int, user_id: int) -> bool:
    stmt = select(likes_table).where(
        (likes_table.c.tweet_id == tweet_id) & (likes_table.c.user_id == user_id))
    return await session.scalar(stmt)


async def add_like_in_db(session: AsyncSession, tweet: Tweet, user_id: int) -> bool | None:
    exists = await check_likes(session, tweet.tweet_id, user_id)
    if exists:
        return False

    user = await get_full_user_data(session, user_id)
    user.likes.append(tweet)
    session.add_all(user.likes)
    await session.commit()


async def delete_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    exists = await check_likes(session, tweet.tweet_id, user.id)
    if not exists:
        return False
    user = await get_full_user_data(session, user.id)
    user.likes.remove(tweet)
    await session.commit()


async def check_followed(session: AsyncSession, user_id: int, user_followed_id: int) -> bool:
    stmt = select(followers).where(
        (followers.c.follower_id == user_id) & (followers.c.followed_id == user_followed_id))
    return await session.scalar(stmt)


async def add_followed(session: AsyncSession, user_id, user_followed):
    check_follow = await check_followed(session, user_id, user_followed.id)
    if check_follow:
        return False

    user = await get_user_data_followed(session, user_id)
    user.followed.append(user_followed)
    session.add_all(user.followed)
    await session.commit()


async def remove_followed(session: AsyncSession, user_id, user_followed):
    check_follow = await check_followed(session, user_id, user_followed.id)
    if not check_follow:
        return False

    user = await get_user_data_followed(session, user_id)
    user.followed.remove(user_followed)
    await session.commit()


async def get_image_url(session: AsyncSession, image_id_list: List[int]):
    stmt = select(Image).where(
        Image.id.in_(image_id_list)
    )
    return await session.scalars(stmt)
