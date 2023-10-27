from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi.security import APIKeyHeader

from database.crud import get_user_by_api_key, get_user_by_id, remove_followed, add_followed
from database.database import get_async_session
from database.models import User
from schemas import ReturnUserSchema, Message, SuccessSchema
from services import get_user_info, generate_error_message, return_user_not_found

router_us = APIRouter(prefix="/api/users")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@router_us.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema
)
async def user_info(
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    return await get_user_info(session, user.id)


@router_us.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema
)
async def user_by_id_info(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session)
):
    await get_user_by_api_key(session, api_key)
    search_user: User | None = await get_user_by_id(session, user_id)
    return await get_user_info(session, search_user.id)


@router_us.delete(
    "/{user_id}/follow",
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema
)
async def remove_follow(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    user_followed: User | None = await get_user_by_id(session, user_id)

    await remove_followed(session, user.id, user_followed)
    return {"result": True}


@router_us.post(
    "/{user_id}/follow",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema
)
async def add_follow(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    user_followed: User | None = await get_user_by_id(session, user_id)
    await add_followed(session, user.id, user_followed)
    return {"result": True}
