"""We describe schemes for checking the reception
and delivery of data when working with users."""
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    """Schema for returning user information."""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")


class UserSchemaLikes(BaseModel):
    """The scheme for obtaining information about the user for likes
    differs from the previous one in the ID name."""

    model_config = ConfigDict(from_attributes=True)
    user_id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")


class UserSchemaFull(BaseModel):
    """Schema for complete user information."""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    following: List[UserSchema] = Field(
        ...,
        description="List following",
    )
    followers: List[UserSchema] = Field(
        ...,
        description="List followers",
    )


class ReturnUserSchema(BaseModel):
    """A schema for returning the result and complete information about the user."""

    model_config = ConfigDict(from_attributes=True)
    result: bool = Field(..., description="Result, true or false")
    user: UserSchemaFull = Field(..., description="User object")


class AddUserSchema(BaseModel):
    """Scheme for adding a user."""
    api_key: str = Field(
        ...,
        description="Some user api_key",
        min_length=5,
        max_length=30,
    )
    name: str = Field(..., description="User's name")
