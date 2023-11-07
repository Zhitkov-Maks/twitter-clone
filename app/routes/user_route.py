from typing import Dict

from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud.user import (
    add_followed,
    get_user_by_api_key,
    get_user_by_id,
    remove_followed,
)
from models.db_conf import get_async_session
from models.model import User
from schemas.tweet_schema import SuccessSchema
from schemas.user_schema import ReturnUserSchema
from service import get_user_info

route_us = APIRouter(prefix='/api/users')
api_key_header = APIKeyHeader(name='api-key', auto_error=False)


@route_us.get(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema,
)
async def user_info(
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Get information about the current user."""
    user: User | None = await get_user_by_api_key(session, api_key)
    return await get_user_info(session, user)


@route_us.get(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=ReturnUserSchema,
)
async def user_by_id_info(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Get information about a user by ID."""
    await get_user_by_api_key(session, api_key)
    search_user: User | None = await get_user_by_id(session, user_id)
    return await get_user_info(session, search_user)


@route_us.delete(
    '/{user_id}/follow',
    status_code=status.HTTP_200_OK,
    response_model=SuccessSchema,
)
async def remove_follow(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Unfollow user."""
    user: User = await get_user_by_api_key(session, api_key)
    user_followed: User = await get_user_by_id(session, user_id)

    await remove_followed(session, user.id, user_followed)
    return {'result': True}


@route_us.post(
    '/{user_id}/follow',
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessSchema,
)
async def add_follow(
        user_id: int,
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session),
) -> Dict[str, bool]:
    """Add subscription."""
    user: User = await get_user_by_api_key(session, api_key)
    user_followed: User = await get_user_by_id(session, user_id)
    await add_followed(session, user.id, user_followed)
    return {'result': True}
