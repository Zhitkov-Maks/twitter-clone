"""A module for working with data, such as saving pictures and generating a response to the user."""
from pathlib import Path
from typing import Dict, List

import aiofiles

from config import allowed_types
from crud.tweet import get_all_tweet_followed
from crud.user import get_full_user_data
from fastapi import HTTPException, UploadFile
from models.model import Image, User
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

OUT_PATH = Path(__file__).parent / "./dist/images/"
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def read_and_write_image(
    session: AsyncSession,
    img: UploadFile,
) -> int:
    """The function reads and saves the file to storage."""
    if img.content_type in allowed_types:
        file_location = "{0}/{1}".format(OUT_PATH, img.filename)
        file_read = await img.read()

        async with aiofiles.open(file_location, "wb") as file_object:
            await file_object.write(file_read)
        return await add_image_in_db(session, img.filename)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail={
            "result": False,
            "error_type": "UNSUPPORTED_MEDIA_TYPE",
            "error_message": "File type is not supported",
        },
    )


async def tweet_constructor(
    session: AsyncSession, user_id: int
) -> Dict[str, bool | List[Dict[str, int | str]]]:
    """Function for collecting complete information on tweets.
    Returns a response that satisfies the frontend."""
    tweet_list = []
    tweets = await get_all_tweet_followed(session, user_id)
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
    session: AsyncSession, user
) -> Dict[str, bool | Dict[str, int | str | List[User]]]:
    """Function for collecting complete information on the user."""
    user_full: User = await get_full_user_data(session, user)
    return {
        "result": True,
        "user": {
            "id": user_full.id,
            "name": user_full.name,
            "followers": user_full.follower,
            "following": user_full.followed,
        },
    }


async def add_image_in_db(session: AsyncSession, url: str | None) -> int:
    """Function for adding a picture to the database."""
    img: Image = Image(url=url)
    session.add(img)
    await session.commit()
    return img.id
