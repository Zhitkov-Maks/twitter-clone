from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud.image import transform_image_id_in_image_url
from crud.user import get_full_user_data
from models.model import Tweet
from models.model import User, likes_table
from schemas.tweet_schema import AddTweetSchema


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
    """Function for receiving tweets sorted by."""
    stmt = select(
        Tweet, func.count(likes_table.c.user_id).label('likes'),
    ).join(
        likes_table, (likes_table.c.tweet_id == Tweet.tweet_id), isouter=True,
    ).group_by(
        Tweet.tweet_id).order_by(desc('likes')).limit(25)
    # stmt = select(
    #     Tweet, func.count(likes_table.c.user_id).label('likes'),
    # ).join(
    #     followers, (followers.c.followed_id == Tweet.user_id),
    # ).join(
    #     likes_table, (likes_table.c.tweet_id == Tweet.tweet_id), isouter=True,
    # ).where(
    #     followers.c.follower_id == user_id,
    # ).group_by(Tweet.tweet_id).order_by(desc('likes')).limit(25)
    all_tweet = await session.scalars(stmt)
    return all_tweet.unique().all()


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet:
    """Function to get tweet by ID."""
    tweet: Tweet | None = await session.get(Tweet, tweet_id)
    if tweet is not None:
        return tweet
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            'result': False,
            'error_type': 'Not Found',
            'error_message': 'Tweet is not found.',
        },
    )


async def delete_tweet_by_id(session: AsyncSession, tweet: Tweet):
    """Function for deleting a tweet by ID."""
    await session.delete(tweet)
    await session.commit()


async def add_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    """Function for adding likes."""
    try:
        tweet.likes.append(user)
        session.add_all(tweet.likes)
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'result': False,
                'error_type': 'Bad Request',
                'error_message': 'You are already liked it.',
            },
        )


async def delete_like_in_db(session: AsyncSession, tweet: Tweet, user: User):
    """Function for removing likes."""
    try:
        tweet.likes.remove(user)
        await session.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'result': False,
                'error_type': 'Bad Request',
                'error_message': 'You are already deleted it.',
            },
        )
