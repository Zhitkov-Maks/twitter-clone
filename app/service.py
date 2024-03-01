"""A module for working with data, such as saving pictures and generating a response to the user."""
import random
from pathlib import Path
from string import ascii_letters, digits
from typing import Sequence

import aiofiles
from starlette import status

from config import allowed_types
from crud.tweet import get_all_tweet_followed
from crud.user import get_full_user_data
from fastapi import UploadFile, HTTPException
from models.model import Image, User, Tweet
from sqlalchemy.ext.asyncio import AsyncSession

OUT_PATH = Path(__file__).parent / "./dist/images/"
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def generate_sequence() -> str:
    """
    Генерируем последовательность символов для добавления к картинке.

    :return str: Возвращает строку из символов.
    """

    sequence: str = ""
    for index in range(5):
        sequence += random.choice(ascii_letters)
        sequence += random.choice(digits)
    return sequence


async def read_and_write_image(
    session: AsyncSession,
    img: UploadFile,
) -> int:
    """
    Функция читает пришедший файл и сохраняет в хранилище.

    :param session: Сессия для работы с бд.
    :param img: Картинка из формы.
    :return int: Возвращает id сохраненной в бд картинки.
    """

    # Проверяем допустимый ли формат картинки.
    if img.content_type in allowed_types:
        file_name: str = (
            await generate_sequence() + img.filename
            if isinstance(img.filename, str)
            else ".png"
        )
        file_location = "{0}/{1}".format(OUT_PATH, file_name)

        file_read = await img.read()
        async with aiofiles.open(file_location, "wb") as file_object:
            await file_object.write(file_read)

        # Отправляем на сохранение в бд имени картинки.
        return await add_image_in_db(session, file_name)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail={
            "result": False,
            "error_type": "UNSUPPORTED_MEDIA_TYPE",
            "error_message": "File type not supported",
        },
    )


async def tweet_constructor(
    session: AsyncSession,
    user_id: int
) -> dict:
    """
    Формируем правильную структуры с твитами для отправки на фронтенд.

    :param session: Сессия для работы с бд.
    :param user_id: Идентификатор пользователя,
    нужен если будет сортировка твитов от подписчиков.
    :return dict: Возвращаем данные в виде словаря.
    """
    tweet_list = []
    tweets: Sequence[Tweet] = await get_all_tweet_followed(session, user_id)
    for tweet in tweets:
        tweet_data = {
            "id": tweet.tweet_id,
            "content": tweet.tweet_data,
            "attachments": tweet.tweet_media_ids,
            "author": tweet.user,
            "likes": [{"user_id": usr.id, "name": usr.name} for usr in tweet.likes],
        }
        tweet_list.append(tweet_data)
    return {"result": True, "tweets": tweet_list}


async def get_user_info(
    session: AsyncSession,
    user: User
) -> dict:
    """
    Функция для получения полной информации о пользователе, и формирования
    нужной структуры для отправки на фронтенд.

    :param session: Сессия для работы с бд.
    :param user: Объект пользователя для которого будет собираться вся информация.
    :return dict: Возвращаем данные в виде словаря."""
    user_full: User | None = await get_full_user_data(session, user)
    if user_full is not None:
        return {
            "result": True,
            "user": {
                "id": user_full.id,
                "name": user_full.name,
                "followers": user_full.follower,
                "following": user_full.followed,
            },
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "result": False,
            "error_type": "Not Found",
            "error_message": "User is not found.",
        },
    )


async def add_image_in_db(session: AsyncSession, url: str | None) -> int:
    """
    Функция для сохранения имени картинки в бд.

    :param session: Сессия для работы с бд.
    :param url: Имя картинки.
    :return int: id сохраненной картинки.
    """
    img: Image = Image(url=url)
    session.add(img)
    await session.commit()
    return img.id
