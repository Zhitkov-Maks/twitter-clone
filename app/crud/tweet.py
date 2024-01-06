"""Module for database query operations for working with tweets."""
from typing import List

from config import tweet_followers, number_of_tweets
from crud.image import transform_image_id_in_image_url
from crud.user import get_full_user_data

from crud.utils import remove_images
from models.model import Tweet, User, followers, likes_table
from schemas.tweet_schema import AddTweetSchema
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def add_tweet_in_db(
    session: AsyncSession,
    user: User,
    tweet_in: AddTweetSchema,
) -> int:
    """Function to add a new tweet."""
    user = await get_full_user_data(session, user)
    unpack = await transform_image_id_in_image_url(session, tweet_in)
    tweet = Tweet(**unpack)
    user.tweets.append(tweet)
    session.add_all(user.tweets)
    await session.commit()
    return tweet.tweet_id


async def get_all_tweet_followed(session: AsyncSession, user_id: int):
    """Function of receiving tweets sorted by number of likes."""
    if not tweet_followers:
        stmt = (
            select(
                Tweet,
                func.count(likes_table.c.user_id).label("likes"),
            )
            .join(
                likes_table,
                (likes_table.c.tweet_id == Tweet.tweet_id),
                isouter=True,
            )
            .group_by(Tweet.tweet_id)
            .order_by(desc("likes"))
            .limit(number_of_tweets)
        )
    else:
        stmt = (
            select(
                Tweet,
                func.count(likes_table.c.user_id).label("likes"),
            )
            .join(
                followers,
                (followers.c.followed_id == Tweet.user_id),
            )
            .join(
                likes_table,
                (likes_table.c.tweet_id == Tweet.tweet_id),
                isouter=True,
            )
            .where(
                followers.c.follower_id == user_id,
            )
            .group_by(Tweet.tweet_id)
            .order_by(desc("likes"))
            .limit(number_of_tweets)
        )
    all_tweet = await session.scalars(stmt)
    return all_tweet.unique().all()


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet | None:
    """Function to get tweet by ID."""
    tweet: Tweet | None = await session.get(Tweet, tweet_id)
    if tweet is not None:
        return tweet
    return None


async def delete_tweet_by_id(session: AsyncSession, tweet: Tweet) -> None:
    """Function for deleting a tweet by ID."""
    list_photo_url: List[str] = tweet.tweet_media_ids
    await remove_images(list_photo_url)
    await session.delete(tweet)
    await session.commit()


async def add_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    """Function for adding likes."""
    add_like = True
    try:
        tweet.likes.append(user)
        session.add_all(tweet.likes)
        await session.commit()
    except IntegrityError:
        add_like = False
    finally:
        return add_like


async def delete_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    """Function for removing likes."""
    remove_tweet = True
    try:
        tweet.likes.remove(user)
        await session.commit()
    except ValueError:
        remove_tweet = False
    finally:
        return remove_tweet
