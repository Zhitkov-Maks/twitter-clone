from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi.security import APIKeyHeader

from database.crud import get_user_by_api_key, get_user_by_id, remove_followed, add_followed
from database.database import db_helper
from database.models import User
from schemas import ReturnUserSchema
from services import get_user_info, generate_error_message

router_us = APIRouter(prefix="/api/users")
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@router_us.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema
)
async def user_info(
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    result = await get_user_info(session, user.id)
    return result


@router_us.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema
)
async def user_by_id_info(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    await get_user_by_api_key(session, api_key)
    result = await get_user_info(session, user_id)
    return result


@router_us.delete(
    "/{user_id}/follow",
    status_code=status.HTTP_200_OK
)
async def remove_follow(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    user_followed: User | None = await get_user_by_id(session, user_id)

    removed = await remove_followed(session, user.id, user_followed)
    if removed is None:
        return {"result": True}
    return await generate_error_message(400, "Bad Request", "You've not followed")


@router_us.post(
    "/{user_id}/follow",
    status_code=status.HTTP_201_CREATED
)
async def add_follow(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user: User | None = await get_user_by_api_key(session, api_key)
    user_followed: User | None = await get_user_by_id(session, user_id)
    added = await add_followed(session, user.id, user_followed)
    if added is None:
        return {"result": True}
    return await generate_error_message(409, "Conflict", "You've already followed")
