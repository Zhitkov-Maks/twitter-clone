"""We describe routes for requests related to users."""
from typing import Dict, List

from starlette.responses import JSONResponse

from crud.user import (
    add_followed,
    get_user_by_api_key,
    get_user_by_id,
    remove_followed,
)
from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from models.db_conf import get_async_session
from models.model import User
from schemas.tweet_schema import SuccessSchema, ErrorSchema
from schemas.user_schema import ReturnUserSchema
from service import get_user_info
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

route_us = APIRouter(prefix="/api/users")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@route_us.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema,
    tags=["users"],
)
async def get_user_info_by_api_key(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool | dict[str, int | str | List[User]]]:
    """Get information about the current user.
    The user is located by the api-key one who came to the headers"""

    user: User = await get_user_by_api_key(session, api_key)
    return await get_user_info(session, user)


@route_us.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema,
    responses={404: {"model": ErrorSchema}},
    tags=["users"],
)
async def get_user_info_by_id(
    user_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool | dict[str, int | str | List[User]]] | JSONResponse:
    """Get information about a user by ID."""

    await get_user_by_api_key(session, api_key)

    search_user: User | None = await get_user_by_id(session, user_id)
    if search_user is None:
        return JSONResponse(
            status_code=404,
            content={
                "result": False,
                "error_type": "Not Found",
                "error_message": "User is not found",
            },
        )
    return await get_user_info(session, search_user)


@route_us.delete(
    "/{user_id}/follow",
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema,
    responses={404: {"model": ErrorSchema}},
    tags=["users"],
)
async def remove_follow(
    user_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool] | JSONResponse:
    """Unsubscribe from a user."""
    user: User = await get_user_by_api_key(session, api_key)

    user_followed: User | None = await get_user_by_id(session, user_id)
    if user_followed is None:
        return JSONResponse(
            status_code=404,
            content={
                "result": False,
                "error_type": "Not Found",
                "error_message": "User is not found",
            },
        )

    remove: bool = await remove_followed(session, user.id, user_followed)
    if not remove:
        return JSONResponse(
            status_code=404,
            content={
                "result": False,
                "error_type": "Not Found",
                "error_message": "You are not following this user.",
            },
        )

    return {"result": True}


@route_us.post(
    "/{user_id}/follow",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema,
    responses={400: {"model": ErrorSchema}, 404: {"model": ErrorSchema}},
    tags=["users"],
)
async def add_follow(
    user_id: int,
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool] | JSONResponse:
    """Add subscription."""

    user: User = await get_user_by_api_key(session, api_key)
    if user_id == user.id:
        return JSONResponse(
            status_code=400,
            content={
                "result": False,
                "error_type": "Bad request",
                "error_message": "You can't subscribe to yourself.",
            },
        )

    user_followed: User | None = await get_user_by_id(session, user_id)
    if user_followed is None:
        return JSONResponse(
            status_code=404,
            content={
                "result": False,
                "error_type": "Not Found",
                "error_message": "User is not found",
            },
        )

    followed: bool = await add_followed(session, user.id, user_followed)
    if not followed:
        return JSONResponse(
            status_code=400,
            content={
                "result": False,
                "error_type": "Bad request",
                "error_message": "Yoy already subscribed this user",
            },
        )

    return {"result": True}
