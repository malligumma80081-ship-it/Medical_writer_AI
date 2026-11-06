import uuid

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def create_access_token(user_id: str, role: str) -> str:

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.access_token_expire_minutes
        ),
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(user_id: str):

    now = datetime.now(timezone.utc)

    jti = str(uuid.uuid4())

    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(
            days=settings.refresh_token_expire_days
        ),
        "jti": jti,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    expires_at = now + timedelta(
        days=settings.refresh_token_expire_days
    )

    return token, jti, expires_at


def decode_token(token: str):

    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": [
                "sub",
                "exp",
                "iat",
                "jti",
                "type",
            ]
        },
    )