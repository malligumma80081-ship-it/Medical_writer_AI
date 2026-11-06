from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from jwt.exceptions import InvalidTokenError

from app.db.session import get_db

from app.models.user import User

from app.core.config import settings

from app.services.token_service import decode_token
import uuid


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = decode_token(token)

        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            raise credentials_exception

        user_id = uuid.UUID(user_id)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_roles(*allowed_roles: str):

    def role_checker(
        current_user: User = Depends(get_current_user),
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker