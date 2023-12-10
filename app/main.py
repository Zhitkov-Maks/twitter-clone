"""
The application initialization and module
also contains an endpoint for loading images.
"""
from typing import Dict

from crud.user import get_user_by_api_key
from fastapi import Depends, FastAPI, File, Security, UploadFile
from fastapi.security import APIKeyHeader
from models.db_conf import get_async_session
from routes.tweet_route import route_tw
from routes.user_route import route_us
from schemas.tweet_schema import ReturnImageSchema
from service import read_and_write_image
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from py_fastapi_logging.middlewares.logging import LoggingMiddleware

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "tweets",
        "description": "Manage tweets.",
    },
    {"name": "images", "description": "Operations with images"},
]

app = FastAPI(
    title="TWITTER CLONE",
    description="Корпоративный аналог твиттер",
    version="0.0.1",
    contact={
        "name": "Maksim Zhitkov",
        "email": "m-zhitkov@inbox.com",
    },
)
app.add_middleware(LoggingMiddleware, app_name="twitter-clone.log")

app.include_router(route_us)
app.include_router(route_tw)
api_key_header = APIKeyHeader(
    name="api-key",
    auto_error=False,
)


@app.post(
    "/api/medias",
    status_code=status.HTTP_201_CREATED,
    response_model=ReturnImageSchema,
    tags=["images"],
)
async def save_image(
    file: UploadFile = File(...),
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, int]:
    """Function save the image."""
    await get_user_by_api_key(session, api_key)
    image_id: int = await read_and_write_image(session, file)
    return {"result": True, "media_id": image_id}
