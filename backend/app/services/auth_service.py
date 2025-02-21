from datetime import timedelta

from app.core.config import settings
from app.core.security import (
    create_refresh_token,
    create_token,
    decode_token,
    verify_password,
)
from app.db.models import RefreshToken, User
from fastapi import HTTPException
from sqlalchemy.orm import Session


def authenticate_user(email: str, password: str, db: Session):
    """
    Authenticate user and return access and refresh tokens.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None

    access_token = create_token(
        {"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(refresh_token: str, db: Session):
    """
    Refresh access token using the refresh token.
    """
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        return None

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        return None

    new_access_token = create_token(
        {"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return new_access_token


def logout_user(refresh_token: str, db: Session):
    """
    Logout user by invalidating the refresh token.
    """
    deleted_count = (
        db.query(RefreshToken).filter(RefreshToken.token == refresh_token).delete()
    )
    db.commit()

    if deleted_count == 0:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
