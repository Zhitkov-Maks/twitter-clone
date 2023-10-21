from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Base(BaseModel):
    ...


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
        default=[],
        description="List of picture IDs"
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


class ReturnUserSchema(Base):
    model_config = ConfigDict(from_attributes=True)
    result: bool = Field(
        ...,
        description="Result, true or false"
    )
    user: UserSchema = Field(
        ...,
        description="User object"
    )
    following: List[UserSchema] = Field(
        ...,
        description="List following"
    )
    followers: List[UserSchema] = Field(
        ...,
        description="List followers"
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


class AttachmentsSchema(Base):
    url: str


class AddUserSchema(BaseModel):
    name: str = Field()
    api_key: str = Field()


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
    likes: List[UserSchema] = Field(
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
