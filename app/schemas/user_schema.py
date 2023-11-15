from typing import List

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    """Schema for user information."""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")


class UserSchemaLikes(BaseModel):
    """Scheme for getting app_users likes."""

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
    """Scheme for returning app_users."""

    model_config = ConfigDict(from_attributes=True)
    result: bool = Field(..., description="Result, true or false")
    user: UserSchemaFull = Field(..., description="User object")
