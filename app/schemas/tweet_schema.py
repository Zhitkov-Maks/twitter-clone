from typing import List

from pydantic import BaseModel, Field
from schemas.user_schema import UserSchema, UserSchemaLikes

MAX_LENGTH_TWEET = 10000


class SuccessSchema(BaseModel):
    """Return scheme True."""

    result: bool


class Message(BaseModel):
    """Schema for returned errors."""

    result: bool = Field(..., description='Response status')
    error_type: str = Field(..., description='Type error')
    error_message: str = Field(..., description='message')


class AddTweetSchema(BaseModel):
    """Schema for adding tweet."""

    tweet_data: str = Field(
        ...,
        description='Tweet content',
        min_length=10,
        max_length=MAX_LENGTH_TWEET,
    )
    tweet_media_ids: List[int] = Field(
        description="""Photos from the form are loaded automatically,
                       and tweet_media_ids are substituted with IDs of
                       photos saved in the database."""
    )


class ReturnAddTweetSchema(BaseModel):
    """Scheme for returned a tweet."""

    result: bool = Field(..., description='Result, true or false')
    tweet_id: int = Field(..., description='ID созданного твита.')


class ReturnImageSchema(BaseModel):
    """Scheme for returning pictures."""

    result: bool = Field(..., description='Result, true or false')
    media_id: int = Field(..., description='ID созданной картинки')


class TweetSchema(BaseModel):
    """Scheme for returned a tweet."""

    id: int = Field(..., description='ID tweet')
    content: str = Field(..., description='Tweet content')
    attachments: List[str] = Field(..., description='List url images')
    author: UserSchema = Field(..., description='User object')
    likes: List[UserSchemaLikes] = Field(
        ...,
        description='List of app_users who liked it',
    )


class ListTweetSchema(BaseModel):
    """Schematic for getting a list of tweets."""

    result: bool = Field(..., description='Result, true or false')
    tweets: List[TweetSchema] = Field(..., description='List tweets')
