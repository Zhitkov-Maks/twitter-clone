from fastapi import FastAPI, Depends, UploadFile, File, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.crud import get_user_by_api_key
from database.settings import get_async_session
from route.tweet_route import route_tw
from route.user_route import route_us
from schemas import ReturnImageSchema
from services import read_and_write_image

app = FastAPI()
app.include_router(route_us)
app.include_router(route_tw)
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


@app.post(
    "/api/medias", status_code=status.HTTP_201_CREATED, response_model=ReturnImageSchema
)
async def add_image(
    file: UploadFile = File(...),
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
):
    await get_user_by_api_key(session, api_key)
    image_id: int = await read_and_write_image(session, file)
    return {"result": True, "media_id": image_id}
