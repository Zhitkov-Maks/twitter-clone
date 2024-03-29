"""
The application initialization and module
also contains an endpoint for loading images.
"""
from typing import Dict

from starlette.responses import JSONResponse

from crud.user import get_user_by_api_key
from fastapi import Depends, FastAPI, File, Security, UploadFile
from fastapi.security import APIKeyHeader
from models.db_conf import get_async_session
from routes.tweet_route import route_tw
from routes.user_route import route_us
from schemas.tweet_schema import ReturnImageSchema, ErrorSchema
from service import read_and_write_image
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

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
        "name": "Максим Житков",
        "email": "m-zhitkov@inbox.ru",
    },
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

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
    responses={415: {"model": ErrorSchema}},
    tags=["images"],
)
async def save_image(
    file: UploadFile = File(...),
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, int] | JSONResponse:
    """
    Функция принимает файл и отправляет его на сохранение.
    При успешной обработке возвращает словарь в котором будет id сохраненной картинки.

    :param file: Картинка из формы
    :param api_key: api_key для аутентификации пользователя.
    :param session: Сессия для работы с базой данных.
    :return Dict | JSONResponse: При успешном сохранении возвращает словарь,
    в случае ошибки JSONResponse
    """

    # Проверяем если пришедший api_key в базе данных с пользователями, если не будет
    # найден пользователь то будет проброшена ошибка.
    await get_user_by_api_key(session, api_key)

    # Отравляем на сохранение картинки в хранилище, и записи данных о картинке в бд.
    image_id: int = await read_and_write_image(session, file)
    return {"result": True, "media_id": image_id}
