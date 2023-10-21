from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from database.crud import (
    get_user_by_api_key,
    delete_tweet_by_id,
    add_like_in_db,
    get_tweet_by_id,
    delete_like_in_db,
    get_user_by_id,
    add_followed,
    remove_followed,
    add_tweet_in_db
)
from database.database import db_helper
from database.models import User, Tweet, Base, Image
from schemas import (
    AddTweetSchema,
    ReturnAddTweetSchema,
    Message,
    ReturnUserSchema, AddUserSchema, ReturnImageSchema, ListTweetSchema
)
from services import tweet_constructor, get_user_info, read_and_write_image, generate_error_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.post(
    "/api/tweets",
    status_code=status.HTTP_201_CREATED,
    response_model=ReturnAddTweetSchema
)
async def add_tweets(
        tweet_in: AddTweetSchema,
        request: Request,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: int = await add_tweet_in_db(session, user, tweet_in)
    return {"result": True, "tweet_id": tweet}


@app.post(
    "/api/medias",
    status_code=status.HTTP_201_CREATED,
    response_model=ReturnImageSchema
)
async def add_image(
        request: Request,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)

):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    image_id: int = await read_and_write_image(session, file)
    return {"result": True, "media_id": image_id}


@app.delete(
    "/api/tweets/{tweet_id}",
    status_code=status.HTTP_200_OK,
    responses={403: {"model": Message}}
)
async def delete_tweet(
        request: Request,
        tweet_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet = await get_tweet_by_id(session, tweet_id)

    if tweet.user_id != user.id:
        return generate_error_message(403, "Forbidden", "You can't delete this tweet")

    await delete_tweet_by_id(session, tweet)
    return {"result": True}


@app.post(
    "/api/tweets/{tweet_id}/likes",
    status_code=status.HTTP_201_CREATED,
)
async def add_likes(
        request: Request,
        tweet_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet = await get_tweet_by_id(session, tweet_id)
    result = await add_like_in_db(session, tweet, user.id)
    if result:
        return {"result": True}
    return JSONResponse(status_code=400, content={"result": False})


@app.delete(
    "/api/tweets/{tweet_id}/likes",
    status_code=status.HTTP_200_OK
)
async def delete_likes(
        request: Request,
        tweet_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    tweet: Tweet | None = await get_tweet_by_id(session, tweet_id)

    await delete_like_in_db(session, tweet, user)
    return {"result": True}


@app.post(
    "/api/users/{user_id}/follow",
    status_code=status.HTTP_201_CREATED
)
async def add_follow(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    user_followed: User | None = await get_user_by_id(session, user_id)
    await add_followed(session, user.id, user_followed)
    return {"result": True}


@app.delete(
    "/api/users/{user_id}/follow",
    status_code=status.HTTP_200_OK
)
async def remove_follow(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    user_followed: User | None = await get_user_by_id(session, user_id)

    await remove_followed(session, user.id, user_followed)
    return {"result": True}


@app.get(
    "/api/tweets",
    status_code=status.HTTP_200_OK,
    response_model=ListTweetSchema
)
async def get_all_tweets(
        request: Request,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    result = await tweet_constructor(session, user.id)
    return result


@app.get(
    "/api/users/me",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema
)
async def user_info(
        request: Request,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    user: User | None = await get_user_by_api_key(session, api_key)
    result = await get_user_info(session, user.id)
    return result


@app.get(
    "/api/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema
)
async def user_by_id_info(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    api_key: str = request.headers.get("api-key")
    await get_user_by_api_key(session, api_key)
    result = await get_user_info(session, user_id)
    return result


@app.post("/user/me",
          response_model=AddUserSchema,
          status_code=status.HTTP_201_CREATED)
async def add_user(
        user_in: AddUserSchema,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = User(**user_in.model_dump())
    session.add(user)
    await session.commit()
    return user


# location
# ~ * \.(jpeg | png | jpg)$ {
#     root / usr / share / nginx / html / images /;
# autoindex
# on;
# }
