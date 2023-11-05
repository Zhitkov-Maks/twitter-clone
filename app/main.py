"""
The application initialization.

The application initialization and module
also contains an endpoint for loading images.
"""

from fastapi import Depends, FastAPI, File, HTTPException, Security, UploadFile
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud.user import get_user_by_api_key
from models.db_conf import get_async_session
from routes.tweet_route import route_tw
from routes.user_route import route_us
from schemas.tweet_schema import ReturnImageSchema
from service import read_and_write_image

app = FastAPI()
app.include_router(route_us)
app.include_router(route_tw)
api_key_header = APIKeyHeader(
    name='api-key',
    auto_error=False,
)


@app.post(
    '/api/medias',
    status_code=status.HTTP_201_CREATED,
    response_model=ReturnImageSchema,
)
async def add_image(
        file: UploadFile = File(...),
        api_key: str = Security(api_key_header),
        session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Endpoint will save the image.

    :param session: AsyncSession for working with a database.
    :param api_key: User's api-key.
    :param file: File from form.

    :return: We return data in the form dict.

    """
    await get_user_by_api_key(session, api_key)
    image_url: int | HTTPException = await read_and_write_image(session, file)
    return {'result': True, 'media_id': image_url}
