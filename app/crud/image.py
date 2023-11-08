from typing import Any, List

from sqlalchemy import ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.model import Image
from schemas.tweet_schema import AddTweetSchema


async def transform_image_id_in_image_url(
    session: AsyncSession,
    tweet_in: AddTweetSchema,
):
    """Save the image name instead of the ID."""
    unpack = tweet_in.model_dump()
    media = await get_image_url(session, unpack["tweet_media_ids"])
    unpack["tweet_media_ids"] = list(media)
    return unpack


async def get_image_url(
    session: AsyncSession,
    image_id_list: List[int],
) -> ScalarResult[int]:
    """Function return URL from ID."""
    stmt = select(Image.url).where(Image.id.in_(image_id_list))
    return await session.scalars(stmt)
