from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        alias="fullName",
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
    )

    profile_image_url: str = Field(
        default="",
        max_length=500,
        alias="profileImageUrl",
    )


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=1,
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: int

    full_name: str = Field(
        serialization_alias="fullName",
    )

    email: EmailStr

    profile_image_url: str = Field(
        serialization_alias="profileImageUrl",
    )

    created_at: datetime = Field(
        serialization_alias="createdAt",
    )

    updated_at: datetime = Field(
        serialization_alias="updatedAt",
    )


class AuthResponse(BaseModel):
    user: UserResponse
    token: str