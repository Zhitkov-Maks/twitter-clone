from typing import List

import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from database.crud import get_full_user_data, get_all_tweet_followed, add_image_in_db, get_image_url


async def generate_error_message(code: int, type_err: str, message: str):
    return JSONResponse(status_code=code, content={
        "result": False,
        'error_type': type_err,
        "error_message": message
    })


async def read_and_write_image(session: AsyncSession, file: UploadFile):
    allowed_types = ("image/jpg", "image/png", "image/jpeg", "image/webp")
    if file.content_type in allowed_types:
        file_location = f"static/images/{file.filename}"
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


async def tweet_constructor(session: AsyncSession, user_id) -> dict:
    tweet_list: List[dict] = []
    await get_full_user_data(session, user_id)
    tweets = await get_all_tweet_followed(session, user_id)
    for tweet in tweets:
        attachments = await get_image_url(session, tweet.tweet_media_ids)
        tweet_data: dict = {
            "id": tweet.tweet_id,
            "content": tweet.tweet_data,
            "attachments": [attachment.url for attachment in attachments],
            "author": tweet.user,
            "likes": [usr for usr in tweet.likes]
        }
        tweet_list.append(tweet_data)
    final_result = {
        "result": True,
        "tweets": tweet_list
    }
    return final_result


async def get_user_info(session: AsyncSession, user_id) -> dict:
    user = await get_full_user_data(session, user_id)
    final_result = {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name
        },
        "following": [usr for usr in user.followed],
        "followers": [usr for usr in user.follower]
    }
    return final_result
