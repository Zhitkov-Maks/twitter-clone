"""We describe schemes for checking the reception and
delivery of data when working with tweets."""
from typing import List

from pydantic import BaseModel, Field

from config import max_length_tweet, min_length_tweet
from schemas.user_schema import UserSchema, UserSchemaLikes


class ErrorSchema(BaseModel):
    """Scheme for returning errors to the client"""

    result: str
    error_type: str
    error_message: str


class SuccessSchema(BaseModel):
    """The circuit returns true if everything was successful."""

    result: bool


class AddTweetSchema(BaseModel):
    """Schema for adding tweet."""

    tweet_data: str = Field(
        ...,
        description="Some important message",
        min_length=min_length_tweet,
        max_length=max_length_tweet,
    )
    tweet_media_ids: List[int] = Field(
        description="""Photos from the form are loaded automatically,
                       and tweet_media_ids are substituted with IDs of
                       photos saved in the database."""
    )


class ReturnAddTweetSchema(BaseModel):
    """A scheme to return a successful save of a tweet."""

    result: bool = Field(..., description="Result, true or false")
    tweet_id: int = Field(..., description="ID созданного твита.")


class ReturnImageSchema(BaseModel):
    """A scheme to return a successful save of image."""

    result: bool = Field(..., description="Result, true or false")
    media_id: int = Field(..., description="ID созданной картинки")


class TweetSchema(BaseModel):
    """A circuit for returning complete information about a tweet."""

    id: int = Field(..., description="ID tweet")
    content: str = Field(..., description="Tweet content")
    attachments: List[str] = Field(..., description="List url images")
    author: UserSchema = Field(..., description="User object")
    likes: List[UserSchemaLikes] = Field(
        ...,
        description="List of app_users who liked it",
    )


class ListTweetSchema(BaseModel):
    """Circuit for returning a list of tweets."""

    result: bool = Field(..., description="Result, true or false")
    tweets: List[TweetSchema] = Field(..., description="List tweets")
