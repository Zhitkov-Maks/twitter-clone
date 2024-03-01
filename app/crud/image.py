"""Module for database query operations with the Image model"""
from typing import List, Dict

from models.model import Image
from schemas.tweet_schema import AddTweetSchema
from sqlalchemy import ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession


async def transform_image_id_in_image_url(
    session: AsyncSession,
    tweet_in: AddTweetSchema,
) -> Dict[str, List[str]]:
    """
    Функция получает список имен картинок из списка id картинок.

    :param session: Сессия для работы с бд.
    :param tweet_in: Пришедшие с frontend данные о твите.
    :return image_ids: Возвращаем данные где вместо списка id в tweet_media_ids будет
    список имен картинок твита.
    """
    unpack: dict = tweet_in.model_dump()
    media: ScalarResult[str] = await get_image_url(session, unpack["tweet_media_ids"])

    # Удаляем данные о картинке из бд, так как они нам больше не нужны.
    await remove_image_id_in_db(session, unpack["tweet_media_ids"])
    unpack["tweet_media_ids"] = list(media)
    return unpack


async def get_image_url(
    session: AsyncSession,
    image_id_list: List[int],
) -> ScalarResult[str]:
    """
    Функция получает список имен картинок.

    :param session: Сессия для работы с бд.
    :param image_id_list: Список id картинок.
    :return image_url: Список имен картинок."""
    stmt = select(Image.url).where(Image.id.in_(image_id_list))
    return await session.scalars(stmt)


async def remove_image_id_in_db(
    session: AsyncSession,
    image_id_list: List[int],
) -> None:
    """
    Функция удаляет данные о картинке из бд.

    :param session: Сессия для работы с бд.
    :param image_id_list: Список id картинок.
    :return None: Ничего не возвращает.
    """
    for img_id in image_id_list:
        stmt = select(Image).where(Image.id == img_id)
        img: Image | None = await session.scalar(stmt)
        if img:
            await session.delete(img)
    await session.commit()
