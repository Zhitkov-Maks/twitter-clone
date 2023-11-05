"""
Module services.

Performs actions that are inappropriate to do at endpoints
"""

from pathlib import Path
from typing import List

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud.tweet import get_all_tweet_followed
from crud.user import get_full_user_data
from models.model import Image

OUT_PATH = Path(__file__).parent / './dist/images/'
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def read_and_write_image(
        session: AsyncSession,
        img: UploadFile,
) -> int | HTTPException:
    """
    Will read and write.

    The function will read the file and
    if the file is valid, it will save it and
    write it to the database.

    :param session: AsyncSession for working with a database.
    :param img: File from form.
    :raise: If the file type is not supported.
    :return: Image's ID
    """
    allowed_types = ('image/jpg', 'image/png', 'image/jpeg')
    if img.content_type in allowed_types:
        file_location = '{0}/{1}'.format(OUT_PATH, img.filename)
        file_read = await img.read()

        async with aiofiles.open(file_location, 'wb') as file_object:
            await file_object.write(file_read)
        return await add_image_in_db(session, img.filename)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail={
            'result': False,
            'error_type': 'UNSUPPORTED_MEDIA_TYPE',
            'error_message': 'File type is not supported',
        },
    )


async def tweet_constructor(session: AsyncSession, user_id: int) -> dict:
    """
    Will assemble a dictionary to satisfy the frontend conditions.

    :param session: AsyncSession for working with a database.
    :param user_id: User's ID
    :return: We return data in the form dict.
    """
    tweet_list: List[dict] = []
    tweets = await get_all_tweet_followed(session, user_id)
    for tweet in tweets:
        tweet_data: dict = {
            'id': tweet.tweet_id,
            'content': tweet.tweet_data,
            'attachments': tweet.tweet_media_ids,
            'author': tweet.user,
            'likes': [
                {'user_id': usr.id, 'name': usr.name}
                for usr in tweet.likes
            ],
        }
        tweet_list.append(tweet_data)
    return {'result': True, 'tweets': tweet_list}


async def get_user_info(session: AsyncSession, user) -> dict:
    """
    Will return complete information about the user.

    :param session: AsyncSession for working with a database.
    :param user: Object user
    :return: We return data in the form dict.
    """
    user = await get_full_user_data(session, user)
    return {
        'result': True,
        'user': {
            'id': user.id,
            'name': user.name,
            'followers': user.follower,
            'following': user.followed,
        },
    }


async def add_image_in_db(session: AsyncSession, url: str) -> int:
    """
    Function for adding a picture to the database.

    :param session: AsyncSession.
    :param url: name images.
    """
    img: Image = Image(url=url)
    session.add(img)
    await session.commit()
    return img.id
