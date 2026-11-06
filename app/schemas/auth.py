import uuid

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class UserRegister(BaseModel):

    full_name: str = Field(
        min_length=3,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=12,
        max_length=128,
    )


class UserResponse(BaseModel):

    id: uuid.UUID

    full_name: str

    email: EmailStr

    role: str

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class TokenResponse(BaseModel):

    access_token: str = Field(
        description="Use this token to authorize API requests."
    )

    refresh_token: str = Field(
        description=(
            "Send this exact value to /auth/refresh to obtain new tokens."
        )
    )

    token_type: str = Field(
        default="bearer",
        description=(
            "Authorization scheme, not a token. Do not send this as "
            "refresh_token."
        ),
    )