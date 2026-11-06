import uuid

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select

from sqlalchemy.orm import Session

from jwt.exceptions import InvalidTokenError

from app.db.session import get_db

from app.models.user import User

from app.models.auth_session import AuthSession

from app.schemas.auth import (
    UserRegister,
    UserResponse,
    TokenResponse,
)

from app.core.security import (
    hash_password,
    verify_password,
)

from app.core.dependencies import get_current_user

from app.services.token_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserRegister,
    db: Session = Depends(get_db),
):

    email = str(payload.email).lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="Email is already registered.",
        )

    user = User(
        full_name=payload.full_name,
        email=email,
        hashed_password=hash_password(payload.password),
        role="MEDICAL_WRITER",
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    email = form_data.username.lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if (
        user is None
        or not verify_password(
            form_data.password,
            user.hashed_password,
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
        )

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="Account is inactive.",
        )

    access_token = create_access_token(
        str(user.id),
        user.role,
    )

    refresh_token, jti, expires_at = (
        create_refresh_token(str(user.id))
    )

    session = AuthSession(
        user_id=user.id,
        jti=jti,
        expires_at=expires_at,
    )

    db.add(session)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_access_token(
    refresh_token: str = Query(
        description=(
            "Paste the refresh_token value returned by /auth/login. "
            "Do not enter token_type ('bearer') or the access_token."
        )
    ),
    db: Session = Depends(get_db),
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired refresh token.",
    )

    try:

        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise credentials_exception

        user_id = uuid.UUID(payload["sub"])
        jti = payload["jti"]

    except (
        InvalidTokenError,
        ValueError,
        KeyError,
        TypeError,
    ):
        raise credentials_exception

    session = db.scalar(
        select(AuthSession)
        .where(AuthSession.jti == jti)
        .with_for_update()
    )

    now = datetime.now(timezone.utc)

    if session is None:
        raise credentials_exception

    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = expires_at.astimezone(timezone.utc)

    if (
        session.revoked_at is not None
        or expires_at <= now
        or session.user_id != user_id
    ):
        raise credentials_exception

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    # Revoke old refresh session before issuing a new one.
    session.revoked_at = now

    access_token = create_access_token(
        str(user.id),
        user.role,
    )

    new_refresh_token, new_jti, expires_at = (
        create_refresh_token(str(user.id))
    )

    new_session = AuthSession(
        user_id=user.id,
        jti=new_jti,
        expires_at=expires_at,
    )

    db.add(new_session)

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/logout")
def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=400,
                detail="Invalid refresh token.",
            )

        jti = payload["jti"]

        if payload.get("sub") != str(current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Token does not belong to this user.",
            )

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
        )

    session = db.scalar(
        select(AuthSession)
        .where(AuthSession.jti == jti)
        .with_for_update()
    )

    if session is None or session.revoked_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Session is already invalid.",
        )

    session.revoked_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Successfully logged out."
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):

    return current_user