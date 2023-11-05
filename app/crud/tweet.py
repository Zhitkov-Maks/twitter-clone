from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud.image import transform_image_id_in_image_url
from crud.user import get_full_user_data
from models.model import Tweet, followers
from models.model import User, likes_table
from schemas.tweet_schema import AddTweetSchema


async def add_tweet_in_db(
        session: AsyncSession,
        user: User,
        tweet_in: AddTweetSchema,
) -> int:
    """
    Function to add a new tweet.

    :param session: AsyncSession
    :param user: User
    :param tweet_in: Data for creating tweet
    """
    user = await get_full_user_data(session, user)
    unpack = await transform_image_id_in_image_url(session, tweet_in)
    tweet = Tweet(**unpack)
    user.tweets.append(tweet)
    session.add_all(user.tweets)
    await session.commit()
    return tweet.tweet_id


async def get_all_tweet_followed(session: AsyncSession, user_id: int):
    """
    Function for receiving tweets sorted by.

    the number of likes from app_users you follow
    :param session: AsyncSession
    :param user_id: User's ID
    """
    # stmt = select(
    #     Tweet, func.count(likes_table.c.user_id).label('likes'),
    # ).join(
    #     likes_table, (likes_table.c.tweet_id == Tweet.tweet_id), isouter=True,
    # ).group_by(Tweet.tweet_id).order_by(desc('likes')).limit(25)
    # all_tweet = await session.scalars(stmt)

    stmt = select(
        Tweet, func.count(likes_table.c.user_id).label('likes'),
    ).join(
        followers, (followers.c.followed_id == Tweet.user_id),
    ).join(
        likes_table, (likes_table.c.tweet_id == Tweet.tweet_id), isouter=True,
    ).where(
        followers.c.follower_id == user_id,
    ).group_by(Tweet.tweet_id).order_by(desc('likes')).limit(25)
    all_tweet = await session.scalars(stmt)
    return all_tweet.unique().all()


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet:
    """
    Function to get tweet by ID.

    :param session: AsyncSession
    :param tweet_id: json with tweet data
    """
    tweet: Tweet | None = await session.get(Tweet, tweet_id)
    if tweet is not None:
        return tweet
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=await create_message(
            'Tweet is not found',
            'Not Found',
        ),
    )


async def delete_tweet_by_id(session: AsyncSession, tweet: Tweet):
    """
    Function for deleting a tweet by ID.

    :param session: AsyncSession
    :param tweet: Tweet
    """
    await session.delete(tweet)
    await session.commit()


async def add_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    """
    Function for adding likes.

    :param session: AsyncSession
    :param tweet: Tweet
    :param user: User
    """
    try:
        tweet.likes.append(user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=await create_message('You have already liked it'),
        )
    session.add_all(tweet.likes)
    await session.commit()


async def delete_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    """
    Function for removing likes.

    :param session: AsyncSession
    :param tweet: Tweet
    :param user: User
    """
    try:
        tweet.likes.remove(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=await create_message('You have already deleted it'),
        )
    await session.commit()


async def create_message(
        err_message: str,
        err_type: str = 'Bad Request',
) -> dict:
    """
    Function to standardize.

    :parameter err_message: Error message.
    :parameter err_type: Error type
    :return: dict.
    """
    return {
        'result': False,
        'error_type': err_type,
        'error_message': err_message,
    }
