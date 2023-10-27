from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Base(BaseModel):
    ...


class SuccessSchema(Base):
    result: bool


class Message(Base):
    result: bool = Field(
        ...,
        description="Response status"
    )
    error_type: str = Field(
        ...,
        description="Type error"
    )
    error_message: str = Field(
        ...,
        description="message"
    )


class ImageSchema(Base):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(
        ...,
        description="Id images"
    )


class AddTweetSchema(Base):
    tweet_data: str = Field(
        ...,
        description="Tweet content",
        min_length=10,
        max_length=10_000
    )
    tweet_media_ids: List[int] = Field(
        description="Photos from the form are loaded automatically, and tweet_media_ids are substituted with IDs of "
                    "photos saved in the database."
    )


class UserSchema(Base):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(
        ...,
        description="User ID"
    )
    name: str = Field(
        ...,
        description="User name"
    )


class UserSchemaFull(Base):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(
        ...,
        description="User ID"
    )
    name: str = Field(
        ...,
        description="User name"
    )
    following: List[UserSchema] = Field(
        ...,
        description="List following"
    )
    followers: List[UserSchema] = Field(
        ...,
        description="List followers"
    )


class UserSchemaLikes(Base):
    model_config = ConfigDict(from_attributes=True)
    user_id: int = Field(
        ...,
        description="User ID"
    )
    name: str = Field(
        ...,
        description="User name"
    )


class ReturnUserSchema(Base):
    model_config = ConfigDict(from_attributes=True)
    result: bool = Field(
        ...,
        description="Result, true or false"
    )
    user: UserSchemaFull = Field(
        ...,
        description="User object"
    )


class ReturnAddTweetSchema(Base):
    result: bool = Field(
        ...,
        description="Result, true or false"
    )
    tweet_id: int = Field(
        ...,
        description="ID созданного твита."
    )


class ReturnImageSchema(Base):
    result: bool = Field(
        ...,
        description="Result, true or false"
    )
    media_id: int = Field(
        ...,
        description="ID созданной картинки"
    )


class TweetSchema(Base):
    id: int = Field(
        ...,
        description="ID tweet"
    )
    content: str = Field(
        ...,
        description="Tweet content"
    )
    attachments: List[str] = Field(
        ...,
        description="List url images"
    )
    author: UserSchema = Field(
        ...,
        description="User object"
    )
    likes: List[UserSchemaLikes] = Field(
        ...,
        description="List of users who liked it"
    )


class ListTweetSchema(Base):
    result: bool = Field(
        ...,
        description="Result, true or false"
    )
    tweets: List[TweetSchema] = Field(
        ...,
        description="List tweets"
    )
