from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(
        ...,
        max_length=320,
        description="The user's email address",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="The user's plaintext password, supplied for hashing",
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        max_length=320,
        description="The user's email address",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The user's password",
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"