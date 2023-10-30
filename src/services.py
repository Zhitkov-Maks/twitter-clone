from pathlib import Path
from typing import List

import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from bd.crud import (
    get_full_user_data,
    get_all_tweet_followed,
    add_image_in_db,
    get_image_url
)

OUT_PATH = Path('./dist/images')
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def read_and_write_image(session: AsyncSession, file: UploadFile):
    allowed_types = ("image/jpg", "image/png", "image/jpeg")
    if file.content_type in allowed_types:
        file_location = f"{OUT_PATH}/{file.filename}"
        content = await file.read()

        async with aiofiles.open(file_location, "wb") as file_object:
            await file_object.write(content)
        result: int = await add_image_in_db(session, file.filename)
        return result

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail={
            "result": False,
            "error_type": "UNSUPPORTED_MEDIA_TYPE",
            "error_message": f"File type is not supported"
        }
    )


async def tweet_constructor(session: AsyncSession, user_id: int) -> dict:
    tweet_list: List[dict] = []
    tweets = await get_all_tweet_followed(session, user_id)
    for tweet in tweets:
        attachments = await get_image_url(session, tweet.tweet_media_ids)
        tweet_data: dict = {
            "id": tweet.tweet_id,
            "content": tweet.tweet_data,
            "attachments": [attachment.url for attachment in attachments],
            "author": tweet.user,
            "likes": [
                {"user_id": usr.id, "name": usr.name} for usr in tweet.likes
            ]
        }
        tweet_list.append(tweet_data)
    response = {
        "result": True,
        "tweets": tweet_list
    }
    return response


async def get_user_info(session: AsyncSession, user) -> dict:
    user = await get_full_user_data(session, user)
    response = {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [usr for usr in user.follower],
            "following": [usr for usr in user.followed]
        }
    }
    return response
