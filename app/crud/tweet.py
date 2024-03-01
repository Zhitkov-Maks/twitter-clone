"""Module for database query operations for working with tweets."""
from typing import List, Dict, Sequence

from fastapi import HTTPException
from starlette import status

from config import tweet_followers, number_of_tweets
from crud.image import transform_image_id_in_image_url
from crud.user import get_full_user_data

from crud.utils import remove_images
from models.model import Tweet, User, followers, likes_table
from schemas.tweet_schema import AddTweetSchema
from sqlalchemy import desc, func, select, ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def add_tweet_in_db(
    session: AsyncSession,
    user: User,
    tweet_in: AddTweetSchema,
) -> int:
    """
    Функция для сбора нужных данных для отправки на сохранение твита, и непосредственно
    сама отправка на сохранение.

    :param session: Сессия для работы с бд.
    :param user: Пользователь, который написал твит.
    :param tweet_in: Данные пришедшие с frontend и прошедшие валидацию.
    :return int: Возвращает id сохраненного твита.
    """
    # Подгружает полные данные о пользователе, иначе будет падать с ошибкой.
    user_full_data: User | None = await get_full_user_data(session, user)
    unpack: Dict[str, List[str]] = await transform_image_id_in_image_url(session, tweet_in)
    tweet: Tweet = Tweet(**unpack)

    if user_full_data is not None:
        user_full_data.tweets.append(tweet)
        session.add_all(user_full_data.tweets)
        await session.commit()
        return tweet.tweet_id

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": "User is not found.",
        },
    )


async def get_all_tweet_followed(
    session: AsyncSession,
    user_id: int
) -> Sequence[Tweet]:
    """Непосредственно запрос в бд для получения списка твитов. Предусмотрено два вида
    сортировки. По умолчанию получаем все твиты отсортированные по количеству лайков, предусмотрен
    так же запрос для получения твитов только от тех пользователей на которых подписан пользователь.

    :param session: Сессия для работы с бд.
    :param user_id: Идентификатор пользователя который создает твит.
    :return Sequence[Tweet]: Возвращаем список твитов.
    """
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
    all_tweet: ScalarResult[Tweet] = await session.scalars(stmt)
    return all_tweet.unique().all()


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Tweet:
    """
    Получение твита по его ID.

    :param session:  Сессия для работы с бд.
    :param tweet_id: Идентификатор твита.
    :return Tweet: Возвращаем в случае успеха найденный твит."""
    tweet: Tweet | None = await session.get(Tweet, tweet_id)
    if tweet is not None:
        return tweet

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": "Tweet with this id not found.",
        },
    )


async def delete_tweet_by_id(session: AsyncSession, tweet: Tweet) -> None:
    """
    Функция удаляет твит, а так же делает запрос на
    удаление картинок этого твита из хранилища.

    :param session: Сессия для работы с бд.
    :param tweet: Непосредственно твит для удаления
    :return None: Ничего не возвращаем.
    """
    list_photo_url: List[str] = tweet.tweet_media_ids
    await remove_images(list_photo_url)
    await session.delete(tweet)
    await session.commit()


async def add_like_in_db(session: AsyncSession, tweet: Tweet, user: User) -> None:
    """
    Функция для добавления лайка к твиту.

    :param session: Сессия для работы с бд.
    :param tweet: Твит к которому нужно добавить лайк.
    :param user: Пользователь, который ставит лайк.
    :return None: Ничего не возвращаем в случае успеха, если лайк уже поставлен
    пробрасываем исключение.
    """
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
                "error_message": "Can't like twice.",
            },
        )


async def delete_like_in_db(session: AsyncSession, tweet: Tweet, user: User) -> None:
    """
    Функция для снятия лайка у твита.

    :param session: Сессия для работы с бд.
    :param tweet: Твит у которого нужно убрать лайк.
    :param user: Пользователь, который хочет удалить лайк.
    :return None: В случае успеха ничего не возвращаем, если лайка
     от этого пользователя нет то пробрасывает исключение."""
    try:
        tweet.likes.remove(user)
        await session.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "result": False,
                "error_type": "Not Found",
                "error_message": "No like found to delete it.",
            },
        )
